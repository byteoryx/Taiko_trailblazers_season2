from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from datatypes.crypto import Balance, Token
from sdk.sql import SQL
from settings.chains import taiko_chain
from settings.config import sleep_between_txs_in_sec
from tools.crypto import get_balance_of, ritsu_swap_tx, get_balance, wait_for_new_balance
from tools.other_utils import sleep_in_range


def ritsu_eth_swap(
        index: int,
        private_key: str,
        source_token: Token,
        destination_token: Token,
        day: str,
        sql: SQL,
        source_amount_to_spend: Balance
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_source_balance = get_balance_of(
        address=account.address, contract=source_token.address, denomination=source_token.denomination
    ) if source_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

    old_destination_balance = get_balance_of(
        address=account.address, contract=destination_token.address, denomination=destination_token.denomination
    ) if destination_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

    if old_source_balance.float >= source_amount_to_spend.float:
        logger.info(f'#{index} | {account.address}: ritsu_swap '
                    f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                    f'${destination_token.ticker}.')

        tx_hash = ritsu_swap_tx(
            private_key=private_key,
            token_out=destination_token,
            token_in=source_token,
            amount_in=source_amount_to_spend.int
        )
        if tx_hash:
            if source_token.ticker != 'ETH':
                new_source_balance = wait_for_new_balance(
                    old_balance=old_source_balance,
                    account=account,
                    chain=taiko_chain,
                    token=source_token
                )
            else:
                new_source_balance = wait_for_new_balance(
                    old_balance=old_source_balance,
                    account=account,
                    chain=taiko_chain
                )

            new_destination_balance = get_balance_of(
                address=account.address, contract=destination_token.address, denomination=destination_token.denomination
            ) if destination_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

            bought_destination_token = new_destination_balance.float - old_destination_balance.float

            if source_token.ticker == 'ETH':
                tx_costs = old_source_balance.float - new_source_balance.float - source_amount_to_spend.float

                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                status = sql.add_bridge_day_report(
                    day_item=DayBridgeItem(
                        id=index,
                        txs=txs,
                        volume=volume,
                        costs=costs + tx_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=index
                )
                logger.info(f'#{index} | {account.address}: ritsu_swap '
                            f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                            f'{round(bought_destination_token, 6)} ${destination_token.ticker} | '
                            f'{taiko_chain.explorer}/{tx_hash} | {status}.')
            else:
                logger.info(f'#{index} | {account.address}: ritsu_swap '
                            f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                            f'{round(bought_destination_token, 6)} ${destination_token.ticker} | '
                            f'{taiko_chain.explorer}/{tx_hash}')

            return True
        else:
            logger.error(f'#{index} | {account.address}: ritsu_swap tx has failed.')

    else:
        logger.warning(f'#{index} | {account.address}: '
                       f'{old_source_balance.float} ${source_token.ticker} > ${destination_token.ticker}, '
                       f'minimum required: {round(source_amount_to_spend.float, 6)} ${source_token.ticker}.')


def ritsu_token_swap(
        index: int,
        private_key: str,
        source_token: Token,
        destination_token: Token,
        day: str,
        sql: SQL,
        source_amount_to_spend: Balance
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_source_balance = get_balance_of(
        address=account.address, contract=source_token.address, denomination=source_token.denomination
    ) if source_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

    old_destination_balance = get_balance_of(
        address=account.address, contract=destination_token.address, denomination=destination_token.denomination
    ) if destination_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

    if old_source_balance.float >= source_amount_to_spend.float:
        logger.info(f'#{index} | {account.address}: ritsu_swap '
                    f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                    f'${destination_token.ticker}.')

        tx_hash = ritsu_swap_tx(
            private_key=private_key,
            token_out=destination_token,
            token_in=source_token,
            amount_in=source_amount_to_spend.int
        )
        if tx_hash:
            if source_token.ticker != 'ETH':
                sleep_in_range(sec_from=120 + sleep_between_txs_in_sec[0], sec_to=120 + sleep_between_txs_in_sec[1])
                new_source_balance = get_balance_of(address=account.address, contract=source_token.address)
            else:
                new_source_balance = wait_for_new_balance(
                    old_balance=old_source_balance,
                    account=account,
                    chain=taiko_chain
                )

            new_destination_balance = get_balance_of(address=account.address, contract=destination_token.address) \
                if destination_token.ticker != 'ETH' else get_balance(address=account.address, rpc=taiko_chain.rpc)

            bought_destination_token = old_destination_balance.float - new_destination_balance.float

            if source_token.ticker == 'ETH':
                tx_costs = old_source_balance.float - new_source_balance.float - source_amount_to_spend.float

                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                status = sql.add_bridge_day_report(
                    day_item=DayBridgeItem(
                        id=index,
                        txs=txs,
                        volume=volume,
                        costs=costs + tx_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=index
                )
                logger.info(f'#{index} | {account.address}: ritsu_swap '
                            f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                            f'{round(bought_destination_token, 6)} ${destination_token.ticker} | '
                            f'{taiko_chain.explorer}/{tx_hash} | {status}.')
            else:
                logger.info(f'#{index} | {account.address}: ritsu_swap '
                            f'{round(source_amount_to_spend.float, 6)} ${source_token.ticker} > '
                            f'{round(bought_destination_token, 6)} ${destination_token.ticker} | '
                            f'{taiko_chain.explorer}/{tx_hash}')

            return True
        else:
            logger.error(f'#{index} | {account.address}: ritsu_swap tx has failed.')

    else:
        logger.warning(f'#{index} | {account.address}: '
                       f'{old_source_balance.float} ${source_token.ticker} > ${destination_token.ticker}, '
                       f'minimum required: {round(source_amount_to_spend.float, 6)} ${source_token.ticker}.')
