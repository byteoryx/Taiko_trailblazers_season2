from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from sdk.sql import SQL
from tools.crypto import get_balance, owlto_deploy_tx
from user_data.chains import taiko_chain


def owlto_deploy_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > 0.0001:
        tx_hash = owlto_deploy_tx(private_key=private_key)
        if tx_hash:
            new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
            new_costs = old_balance.float - new_balance.float

            volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
            status = sql.add_day_report(
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
                f'#{index} | {account.address}: owlto_deploy | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: owlto_deploy tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: owlto_deploy | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: 0.0001 $ETH.')
