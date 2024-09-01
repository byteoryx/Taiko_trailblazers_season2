import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from sdk.sql import SQL
from settings.chains import ChainItem, taiko_chain
from settings.config import leave_on_source
from tools.crypto import get_balance, orbiter_bridge_tx, wait_for_new_balance, xy_bridge_tx


def xy_bridge(
        index: int,
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        day: str,
        sql: SQL,
        multiplier_range: (float, float),
        minimum_transfer: float
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_source_balance = get_balance(address=account.address, rpc=source_chain.rpc)
    old_recipient_balance = get_balance(address=account.address, rpc=recipient_chain.rpc)
    old_total_balance = old_source_balance.float + old_recipient_balance.float

    if old_source_balance.float > leave_on_source + minimum_transfer:
        amount_to_bridge = round(
            (old_source_balance.float - leave_on_source) *
            random.uniform(multiplier_range[0], multiplier_range[1]),
            random.randint(5, 7)
        )
        logger.info(f'#{index} | {account.address}: {old_source_balance.float} $ETH on {source_chain.name}, '
                    f'{amount_to_bridge} $ETH to bridge to {recipient_chain.name}.')

        bridge_tx = xy_bridge_tx(
            private_key=private_key,
            source_chain=source_chain,
            recipient_chain=recipient_chain,
            amount_to_bridge=amount_to_bridge
        )
        if bridge_tx:
            new_recipient_balance = wait_for_new_balance(
                old_balance=old_recipient_balance,
                account=account,
                chain=recipient_chain
            )
            new_source_balance = get_balance(address=account.address, rpc=source_chain.rpc)
            new_total_balance = new_recipient_balance.float + new_source_balance.float
            new_costs = old_total_balance - new_total_balance

            if new_costs < 0 or new_costs > 0.001:
                new_costs = 0.0005

            if source_chain.name != taiko_chain.name:
                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                status = sql.add_bridge_day_report(
                    day_item=DayBridgeItem(
                        id=index,
                        txs=txs + 1,
                        volume=volume + amount_to_bridge,
                        costs=costs + new_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=index
                )
                logger.info(f'#{index} | {account.address}: xy | {source_chain.explorer}/{bridge_tx} | {status}.')
            else:
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
                logger.info(f'#{index} | {account.address}: xy | {source_chain.explorer}/{bridge_tx} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: tx has failed.')
    else:
        logger.warning(f'#{index} | xy | {account.address}: {old_source_balance.float} on {source_chain.name}, '
                       f'minimum required: {round(leave_on_source + minimum_transfer, 6)} $ETH.')
