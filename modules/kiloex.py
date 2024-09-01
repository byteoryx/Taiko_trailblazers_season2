import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from datatypes.crypto import eth_token, Balance, usdc_token
from modules.ritsu import ritsu_single_swap
from sdk.sql import SQL
from settings.chains import taiko_chain
from settings.config import sleep_between_txs_in_sec
from settings.constants import taiko_usdc_contract
from tools.coingecko import get_asset_price
from tools.crypto import get_balance, get_balance_of, meridian_approve_tx, meridian_deposit_tx
from tools.other_utils import sleep_in_range


def kiloex_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.0001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        required_balance_int = int(round(random.uniform(0.01, 0.02), random.randint(3, 6)) * 10 ** 6)

        eth_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        token_balance = get_balance_of(contract=taiko_usdc_contract, address=account.address,
                                       denomination=usdc_token.denomination)

        to_buy_amount_int = required_balance_int - token_balance.int
        if to_buy_amount_int > 0:
            to_buy_amount_float = round(to_buy_amount_int / usdc_token.denomination, 18)
            to_buy_amount_in_usd = to_buy_amount_float
            source_amount_to_spend_float = to_buy_amount_in_usd / get_asset_price(
                ticker=eth_token.coingecko_ticker)
            source_amount_to_spend = Balance(
                float=source_amount_to_spend_float,
                int=int(source_amount_to_spend_float * eth_token.denomination)
            )

            if eth_balance.float > source_amount_to_spend.float:
                ritsu_single_swap(
                    index=index,
                    private_key=private_key,
                    source_token=eth_token,
                    destination_token=usdc_token,
                    day=day,
                    sql=sql,
                    source_amount_to_spend=source_amount_to_spend
                )
            else:
                logger.warning(f'#{index} | {account.address}: ritsu_swap | '
                               f'not enough balance: want to spend: {source_amount_to_spend.float} $ETH, '
                               f'but have only {eth_balance.float} $ETH.')

        token_balance = get_balance_of(contract=taiko_usdc_contract, address=account.address,
                                       denomination=usdc_token.denomination)
        approve_hash = meridian_approve_tx(
            token=usdc_token,
            approve_amount=int(token_balance.int),
            private_key=private_key
        )
        if approve_hash:
            logger.info(
                f'#{index} | {account.address}: approve to spend '
                f'{token_balance.float} ${usdc_token.ticker} | '
                f'{taiko_chain.explorer}/{approve_hash}'
            )
            sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])

            tx_hash = meridian_deposit_tx(private_key=private_key, deposit_int=int(token_balance.int))
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
                    f'#{index} | {account.address}: meridian_deposit | {taiko_chain.explorer}/{tx_hash} | {status}.')
            else:
                logger.error(f'#{index} | {account.address}: meridian_deposit tx has failed.')
        else:
            logger.error(
                f'#{index} | {account.address}: approve to spend '
                f'{token_balance.float} ${usdc_token.ticker} tx has failed.'
            )
    else:
        logger.warning(f'#{index} | {account.address}: meridian | {old_balance.float} $ETH on {taiko_chain.name}, '
                       f'minimum required: {minimum_balance_required} $ETH.')
