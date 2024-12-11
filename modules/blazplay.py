import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem, AccountItem
from sdk.sql import SQL
from tools.crypto import get_balance, blazplay_mint_tx, get_blazplay_balance
from user_data.chains import taiko_chain


def blazplay_main(
        acc: AccountItem,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(acc.private_key)

    blazplay_balance = get_blazplay_balance(address=account.address)
    if blazplay_balance < random.randint(acc.config.modules.blazplay_mint_limit_per_account[0],
                                         acc.config.modules.blazplay_mint_limit_per_account[1]):
        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        if old_balance.float > 0.0001:
            tx_hash = blazplay_mint_tx(private_key=acc.private_key)
            if tx_hash:
                new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                new_costs = old_balance.float - new_balance.float

                volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=acc.id)
                status = sql.add_day_report(
                    day_item=DayBridgeItem(
                        id=acc.id,
                        txs=txs,
                        volume=volume,
                        costs=costs + new_costs,
                        last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    day=day,
                    acc_id=acc.id
                )
                blazplay_balance = get_blazplay_balance(address=account.address)
                logger.info(f'#{acc.id} | {account.address}: blazplay | '
                            f'entry passes: {blazplay_balance} | {taiko_chain.explorer}/{tx_hash} | {status}.')
            else:
                logger.error(f'#{acc.id} | {account.address}: blazplay tx has failed.')
        else:
            logger.warning(
                f'#{acc.id} | {account.address}: blazplay | {old_balance.float} $ETH on {taiko_chain.name}, '
                f'minimum required: 0.0001 $ETH.')
    else:
        logger.info(f'#{acc.id} | {account.address}: blazplay | account already has {blazplay_balance} entry passes.')
