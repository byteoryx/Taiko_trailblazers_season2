import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from datatypes.account import DayBridgeItem
from sdk.sql import SQL
from tools.crypto import get_balance, transfer_tx, wait_for_new_balance, transfer_full_balance
from tools.other_utils import sleep_in_range
from user_data.chains import taiko_chain, ChainItem
from user_data.config import sleep_between_txs_in_sec


def self_transfer_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str,
        multiplier_range: (float, float)
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > 0.001:
        amount_to_send = round(
            old_balance.float *
            random.uniform(multiplier_range[0], multiplier_range[1]),
            random.randint(5, 7)
        )
        tx_hash = transfer_tx(
            private_key=private_key,
            amount_to_send=amount_to_send
        )
        if tx_hash:
            new_balance = wait_for_new_balance(
                old_balance=old_balance,
                account=account,
                chain=taiko_chain
            )
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
            logger.info(f'#{index} | {account.address}: self-transfer {amount_to_send} $ETH | '
                        f'{taiko_chain.explorer}/{tx_hash} | {status}.')
            sleep_in_range(sec_from=10 + sleep_between_txs_in_sec[0], sec_to=10 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{index} | {account.address}: self-transfer tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: self-transfer | {old_balance.float} $ETH on {taiko_chain.name}, '
                       f'minimum required: 0.001 $ETH.')


def burner_transfer_main(
        index: int,
        main_private_key: str,
        burner_private_key: str,
        sql: SQL,
        day: str,
        multiplier_range: (float, float),
        withdraw_only: bool = False
):
    w3 = Web3()

    main_account = w3.eth.account.from_key(main_private_key)
    burner_account = w3.eth.account.from_key(burner_private_key)

    if not withdraw_only:
        old_main_balance = get_balance(address=main_account.address, rpc=taiko_chain.rpc)
        old_burner_balance = get_balance(address=burner_account.address, rpc=taiko_chain.rpc)
        old_total_balance = old_main_balance.float + old_burner_balance.float

        if old_main_balance.float > 0.0001:
            amount_to_send = round(
                old_main_balance.float *
                random.uniform(multiplier_range[0], multiplier_range[1]),
                random.randint(5, 7)
            )
            tx_hash = transfer_tx(
                private_key=main_private_key,
                amount_to_send=amount_to_send,
                address=w3.to_checksum_address(burner_account.address)
            )
            if tx_hash:
                new_burner_balance = wait_for_new_balance(
                    old_balance=old_burner_balance,
                    account=burner_account,
                    chain=taiko_chain
                )
                new_main_balance = get_balance(address=main_account.address, rpc=taiko_chain.rpc)
                new_total_balance = new_burner_balance.float + new_main_balance.float

                new_costs = old_total_balance - new_total_balance
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
                logger.info(f'#{index} | {main_account.address}: '
                            f'transfer {amount_to_send} $ETH to burner {burner_account.address} | '
                            f'{taiko_chain.explorer}/{tx_hash} | {status}.')
                sleep_in_range(sec_from=120 + sleep_between_txs_in_sec[0], sec_to=120 + sleep_between_txs_in_sec[1])
            else:
                logger.error(f'#{index} | {main_account.address}: '
                             f'transfer to burner {burner_account.address} burner tx has failed.')
        else:
            logger.warning(f'#{index} | {main_account.address}: transfer to burner | '
                           f'{old_main_balance.float} $ETH on {taiko_chain.name}, '
                           f'minimum required: 0.0001 $ETH.')

    old_main_balance = get_balance(address=main_account.address, rpc=taiko_chain.rpc)
    old_burner_balance = get_balance(address=burner_account.address, rpc=taiko_chain.rpc)
    old_total_balance = old_main_balance.float + old_burner_balance.float

    if old_burner_balance.float > 0.00001:
        new_main_balance = get_balance(address=main_account.address, rpc=taiko_chain.rpc)

        burner_tx_hash = transfer_full_balance(private_key=burner_private_key, recipient_addr=main_account.address)

        if burner_tx_hash:
            if "not enough balance" in burner_tx_hash:
                logger.info(
                    f'#{index} | {main_account.address}: nothing to transfer from burner {burner_account.address}.'
                )
            else:
                new_main_balance = wait_for_new_balance(
                    old_balance=new_main_balance,
                    account=main_account,
                    chain=taiko_chain
                )
                new_burner_balance = get_balance(address=burner_account.address, rpc=taiko_chain.rpc)
                new_total_balance = new_main_balance.float + new_burner_balance.float
                new_costs = old_total_balance - new_total_balance

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
                logger.info(f'#{index} | {main_account.address}: '
                            f'transfer {old_burner_balance.float} $ETH from burner {burner_account.address} | '
                            f'{taiko_chain.explorer}/{burner_tx_hash} | {status}.')
                sleep_in_range(sec_from=30 + sleep_between_txs_in_sec[0], sec_to=30 + sleep_between_txs_in_sec[1])
        else:
            logger.error(
                f'#{index} | {burner_account.address}: '
                f'transfer {old_burner_balance.float} $ETH from burner {burner_account.address} tx has failed.'
            )


def transfer_main(
        index: int,
        private_key: str,
        address: str,
        multiplier_range: (float, float) = (1, 1),
        transfer_amount: float = 0,
        chain: ChainItem = taiko_chain
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=chain.rpc)
    if old_balance.float > 0.001:
        if transfer_amount:
            amount_to_send = transfer_amount
        else:
            amount_to_send = round(
                old_balance.float *
                random.uniform(multiplier_range[0], multiplier_range[1]),
                random.randint(5, 7)
            )

        tx_hash = transfer_tx(
            private_key=private_key,
            amount_to_send=amount_to_send,
            address=address,
            chain=chain
        )
        if tx_hash:
            new_balance = wait_for_new_balance(
                old_balance=old_balance,
                account=account,
                chain=chain
            )

            logger.info(f'#{index} | {account.address}: transfer to [{address}] {round(amount_to_send, 6)} $ETH | '
                        f'{chain.explorer}/{tx_hash} | new balance {new_balance.float} on {chain.name}.')
            sleep_in_range(sec_from=10 + sleep_between_txs_in_sec[0], sec_to=10 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{index} | {account.address}: transfer to [{address}] tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: transfer to [{address}] | {old_balance.float} $ETH on {chain.name}, '
            f'minimum required: 0.001 $ETH.')
