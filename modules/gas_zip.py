import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem, AccountItem
from sdk.sql import SQL
from tools.crypto import get_balance, wait_for_new_balance, gas_zip_bridge_tx
from user_data.chains import ChainItem, taiko_chain


def gas_zip_bridge(
        account_item: AccountItem,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        day: str,
        sql: SQL,
        multiplier_range: (float, float),
        minimum_transfer: float
):
    w3 = Web3()
    account = w3.eth.account.from_key(account_item.private_key)

    old_source_balance = get_balance(address=account.address, rpc=source_chain.rpc)
    old_recipient_balance = get_balance(address=account.address, rpc=recipient_chain.rpc)
    old_total_balance = old_source_balance.float + old_recipient_balance.float

    if source_chain.name.lower() == 'taiko':
        leave_on_source = account_item.config.common.leave_balance_on_taiko_chain
    else:
        leave_on_source = account_item.config.common.leave_balance_on_source_chains

    if old_source_balance.float > leave_on_source + minimum_transfer:
        amount_to_bridge = round(
            (old_source_balance.float - leave_on_source) *
            random.uniform(multiplier_range[0], multiplier_range[1]),
            random.randint(5, 7)
        )

        bridge_tx = gas_zip_bridge_tx(
            private_key=account_item.private_key,
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
                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=account_item.id)
                status = sql.add_day_report(
                    day_item=DayBridgeItem(
                        id=account_item.id,
                        txs=txs + 1,
                        volume=volume + amount_to_bridge,
                        costs=costs + new_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=account_item.id
                )
                logger.info(
                    f'#{account_item.id} | {account.address}: gas.zip | {source_chain.explorer}/{bridge_tx} | {status}.')
            else:
                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=account_item.id)
                status = sql.add_day_report(
                    day_item=DayBridgeItem(
                        id=account_item.id,
                        txs=txs,
                        volume=volume,
                        costs=costs + new_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=account_item.id
                )
                logger.info(
                    f'#{account_item.id} | {account.address}: gas.zip | {source_chain.explorer}/{bridge_tx} | {status}.')
        else:
            logger.error(f'#{account_item.id} | {account.address}: gas.zip tx has failed.')
    else:
        logger.warning(
            f'#{account_item.id} | gas.zip | {account.address}: {old_source_balance.float} on {source_chain.name}, '
            f'minimum required: {round(leave_on_source + minimum_transfer, 6)} $ETH.')
