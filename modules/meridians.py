import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from datatypes.crypto import eth_token, Balance, usdce_token
from modules.ritsu import ritsu_eth_swap, ritsu_token_swap
from sdk.sql import SQL
from settings.chains import taiko_chain
from settings.config import sleep_between_txs_in_sec
from settings.constants import taiko_usdc_stg_contract, meridian_deposit_contract, ritsu_swap_contract, \
    meridian_deposited_usdc
from tools.coingecko import get_asset_price
from tools.crypto import get_balance, get_balance_of, meridian_approve_tx, meridian_deposit_tx, get_allowance, \
    meridian_withdraw_tx, ritsu_approve_tx
from tools.other_utils import sleep_in_range


def meridian_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.0001
    meridian_deposit_amount = (1.01, 1.1)

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    deposited_usdc_balance = get_balance_of(
        contract=meridian_deposited_usdc,
        address=account.address,
        denomination=10 ** 6
    )
    if deposited_usdc_balance.float < meridian_deposit_amount[0]:

        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        if old_balance.float > minimum_balance_required:
            required_balance_int = int(round(random.uniform(
                meridian_deposit_amount[0], meridian_deposit_amount[1]
            ), random.randint(3, 6)) * usdce_token.denomination)

            eth_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
            token_balance = get_balance_of(contract=taiko_usdc_stg_contract, address=account.address,
                                           denomination=usdce_token.denomination)

            to_buy_amount_int = required_balance_int - token_balance.int
            if to_buy_amount_int > 0:
                to_buy_amount_float = round(to_buy_amount_int / usdce_token.denomination, 18)
                to_buy_amount_in_usd = to_buy_amount_float
                source_amount_to_spend_float = to_buy_amount_in_usd / get_asset_price(
                    ticker=eth_token.coingecko_ticker)
                source_amount_to_spend = Balance(
                    float=source_amount_to_spend_float,
                    int=int(source_amount_to_spend_float * eth_token.denomination)
                )

                if eth_balance.float > source_amount_to_spend.float:
                    tx = ritsu_eth_swap(
                        index=index,
                        private_key=private_key,
                        source_token=eth_token,
                        destination_token=usdce_token,
                        day=day,
                        sql=sql,
                        source_amount_to_spend=source_amount_to_spend
                    )
                    if tx:
                        sleep_in_range(sec_from=120 + sleep_between_txs_in_sec[0],
                                       sec_to=120 + sleep_between_txs_in_sec[1])
                        token_balance = get_balance_of(contract=taiko_usdc_stg_contract, address=account.address,
                                                       denomination=usdce_token.denomination)
                else:
                    logger.warning(f'#{index} | {account.address}: ritsu_swap | '
                                   f'not enough balance: want to spend: {source_amount_to_spend.float} $ETH, '
                                   f'but have only {eth_balance.float} $ETH.')

            allowance = get_allowance(private_key=private_key, token=usdce_token,
                                      spender_address=meridian_deposit_contract)
            if allowance.int < token_balance.int:
                approve_hash = meridian_approve_tx(
                    token=usdce_token,
                    approve_amount=int(token_balance.int),
                    private_key=private_key
                )
                if approve_hash:
                    logger.info(
                        f'#{index} | {account.address}: approve to spend '
                        f'{token_balance.float} $USDCe | '
                        f'{taiko_chain.explorer}/{approve_hash}'
                    )
                    sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
                else:
                    logger.error(
                        f'#{index} | {account.address}: approve to spend '
                        f'{token_balance.float} $USDCe tx has failed.'
                    )

            if token_balance.int:
                tx_hash = meridian_deposit_tx(private_key=private_key, deposit_int=int(token_balance.int))
                if tx_hash:
                    new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                    new_costs = old_balance.float - new_balance.float

                    deposited_usdc_balance = get_balance_of(
                        contract=meridian_deposited_usdc,
                        address=account.address,
                        denomination=10 ** 6
                    )

                    volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                    status = sql.add_bridge_day_report(
                        day_item=DayBridgeItem(
                            id=index,
                            txs=txs,
                            volume=volume,
                            costs=costs + new_costs,
                            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        day=day,
                        acc_id=index
                    )
                    logger.info(
                        f'#{index} | {account.address}: meridian_deposit | deposited: {deposited_usdc_balance.float} $USDCe '
                        f'| {taiko_chain.explorer}/{tx_hash} | {status}.')
                else:
                    logger.error(f'#{index} | {account.address}: meridian_deposit tx has failed.')
            else:
                logger.warning(
                    f'#{index} | {account.address}: meridian | nothing to deposit.')
        else:
            logger.warning(f'#{index} | {account.address}: meridian | {old_balance.float} $ETH on {taiko_chain.name}, '
                           f'minimum required: {minimum_balance_required} $ETH.')
    else:
        logger.warning(f'#{index} | {account.address}: meridian | '
                       f'already deposited {deposited_usdc_balance.float} $USDCe.')


def meridian_withdraw_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    deposited_usdc_balance = get_balance_of(
        contract=meridian_deposited_usdc,
        address=account.address,
        denomination=10 ** 6
    )
    if deposited_usdc_balance.int:
        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        tx_hash = meridian_withdraw_tx(private_key=private_key, withdraw_int=int(deposited_usdc_balance.int))
        if tx_hash:
            new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
            new_costs = old_balance.float - new_balance.float

            volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
            status = sql.add_bridge_day_report(
                day_item=DayBridgeItem(
                    id=index,
                    txs=txs,
                    volume=volume,
                    costs=costs + new_costs,
                    last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
                day=day,
                acc_id=index
            )
            logger.info(
                f'#{index} | {account.address}: meridian_withdraw | {deposited_usdc_balance.float} $USDCe '
                f'| {taiko_chain.explorer}/{tx_hash} | {status}.')
            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{index} | {account.address}: meridian_withdraw tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: meridian_withdraw | nothing to withdraw.')

    usdce_balance = get_balance_of(
        contract=usdce_token.address,
        address=account.address,
        denomination=usdce_token.denomination
    )
    if usdce_balance.int:
        allowance = get_allowance(private_key=private_key, token=usdce_token, spender_address=ritsu_swap_contract)
        if allowance.int < usdce_balance.int:
            approve_hash = ritsu_approve_tx(
                token=usdce_token,
                approve_amount=int(usdce_balance.int),
                private_key=private_key
            )
            if approve_hash:
                logger.info(
                    f'#{index} | {account.address}: approve to spend '
                    f'{usdce_balance.float} $USDCe | '
                    f'{taiko_chain.explorer}/{approve_hash}'
                )
                sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
            else:
                logger.error(
                    f'#{index} | {account.address}: approve to spend '
                    f'{usdce_balance.float} $USDCe tx has failed.'
                )

        ritsu_token_swap(
            index=index,
            private_key=private_key,
            source_token=usdce_token,
            destination_token=eth_token,
            day=day,
            sql=sql,
            source_amount_to_spend=usdce_balance
        )

        usdce_balance = get_balance_of(
            contract=usdce_token.address,
            address=account.address,
            denomination=usdce_token.denomination
        )
    eth_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    logger.info(f'#{index} | {account.address}: {eth_balance.float} $ETH, {usdce_balance.float} $USDCe.')
