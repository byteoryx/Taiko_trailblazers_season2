import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from sdk.sql import SQL
from tools.crypto import (
    get_balance,
    brigade_harvest_tx,
    brigade_spin_tx,
    brigade_capsule_tx,
    brigade_starship_tx,
    brigade_checkin_tx,
    brigade_claim_item_tx
)
from user_data.chains import taiko_chain


def brigade_harvest(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        tx_hash = brigade_harvest_tx(
            private_key=private_key,
        )
        if tx_hash and "you can't harvest yet" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_harvest | you can't harvest yet.")
        elif tx_hash:
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
            logger.info(f'#{index} | {account.address}: brigade_harvest | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_harvest tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: brigade_harvest | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: {minimum_balance_required} $ETH.'
        )


def brigade_spin(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        tx_hash = brigade_spin_tx(
            private_key=private_key,
        )
        if tx_hash and "you can't spin yet" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_spin | you can't spin yet.")
        elif tx_hash:
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
            logger.info(f'#{index} | {account.address}: brigade_spin | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_spin tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: brigade_spin | {old_balance.float} $ETH on {taiko_chain.name}, '
                       f'minimum required: {minimum_balance_required} $ETH.')


def brigade_capsule(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        tx_hash = brigade_capsule_tx(
            private_key=private_key,
        )
        if tx_hash and "you can't pick a capsule yet" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_spin | you can't pick a capsule yet.")
        elif tx_hash:
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
            logger.info(f'#{index} | {account.address}: brigade_capsule | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_capsule tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: brigade_capsule | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: {minimum_balance_required} $ETH.')


def brigade_starship(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        tx_hash = brigade_starship_tx(
            private_key=private_key,
        )
        if tx_hash and "you can't start yet" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_starship | you can't start yet.")
        elif tx_hash:
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
                f'#{index} | {account.address}: brigade_starship | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_starship tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: brigade_starship | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: {minimum_balance_required} $ETH.')


def brigade_checkin(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        tx_hash = brigade_checkin_tx(
            private_key=private_key,
        )
        if tx_hash and "you can't claim yet" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_checkin | you can't claim start yet.")
        elif tx_hash:
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
            logger.info(f'#{index} | {account.address}: brigade_checkin | {taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_checkin tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: brigade_checkin | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: {minimum_balance_required} $ETH.')


def brigade_claim_item(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    minimum_balance_required = 0.00001

    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > minimum_balance_required:
        item_index = random.randint(0, 2)
        tx_hash = brigade_claim_item_tx(
            private_key=private_key,
            item_index=item_index
        )
        if tx_hash and "max claims reached for this product" in tx_hash:
            logger.info(f"#{index} | {account.address}: brigade_claim_item{item_index} | already claimed.")
        elif tx_hash:
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
            logger.info(f'#{index} | {account.address}: brigade_claim_item{item_index} | '
                        f'{taiko_chain.explorer}/{tx_hash} | {status}.')
        else:
            logger.error(f'#{index} | {account.address}: brigade_claim_item{item_index} tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: brigade_claim_item | '
                       f'{old_balance.float} $ETH on {taiko_chain.name}, '
                       f'minimum required: {minimum_balance_required} $ETH.')


def brigade_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    tasks = [
        lambda: brigade_harvest(index=index, private_key=private_key, sql=sql, day=day),
        lambda: brigade_spin(index=index, private_key=private_key, sql=sql, day=day),
        lambda: brigade_capsule(index=index, private_key=private_key, sql=sql, day=day),
        lambda: brigade_starship(index=index, private_key=private_key, sql=sql, day=day),
        lambda: brigade_checkin(index=index, private_key=private_key, sql=sql, day=day),
        # lambda: brigade_claim_item(index=index, private_key=private_key, sql=sql, day=day)
    ]

    random.shuffle(tasks)
    for task in tasks:
        task()
