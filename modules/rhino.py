import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from data.constants import rhino_contracts_path
from datatypes.account import DayBridgeItem, AccountItem
from sdk.sql import SQL
from tools.crypto import get_balance, rhino_tx, rhino_deploy_tx
from tools.other_utils import extract_rhino_contracts, append_to_file_if_not_exists, sleep_in_range
from tools.rhino import get_deployed_contracts
from user_data.chains import taiko_chain


def rhino_gm(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    contracts = extract_rhino_contracts(path=rhino_contracts_path)
    if contracts:
        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        if old_balance.float > 0.001:
            tx_hash = rhino_tx(
                private_key=private_key,
                contract=random.choice(contracts)
            )
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
                logger.info(f'#{index} | {account.address}: rhino_gm | {taiko_chain.explorer}/{tx_hash} | {status}.')
            else:
                logger.error(f'#{index} | {account.address}: rhino_gm tx has failed.')
        else:
            logger.warning(f'#{index} | {account.address}: rhino_gm | {old_balance.float} $ETH on {taiko_chain.name}, '
                           f'minimum required: 0.001 $ETH.')
    else:
        logger.info(f'#{index} | {account.address}: no rhino contracts in "{rhino_contracts_path}".')


def rhino_deploy_main(
        acc: AccountItem,
        index: int,
        private_key: str,
        proxy: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    limit_per_account = random.randint(
        acc.config.modules.rhino_deploy_limit_per_account[0], acc.config.modules.rhino_deploy_limit_per_account[1]
    )

    deployed_contracts = get_deployed_contracts(address=account.address, proxy=proxy)
    if not deployed_contracts or len(deployed_contracts.items) < limit_per_account:
        logger.info(f"#{index} | {account.address}: "
                    f"already deployed {len(deployed_contracts.items)} contracts, minting one more.")

        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        if old_balance.float > 0.0001:
            tx_hash = rhino_deploy_tx(private_key=private_key)
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
                    f'#{index} | {account.address}: rhino_deploy | {taiko_chain.explorer}/{tx_hash} | {status}.')
                sleep_in_range(sec_from=61, sec_to=70)
            else:
                logger.error(f'#{index} | {account.address}: rhino_deploy tx has failed.')

            deployed_contracts = get_deployed_contracts(address=account.address, proxy=proxy)
        else:
            logger.warning(
                f'#{index} | {account.address}: rhino_deploy | {old_balance.float} $ETH on {taiko_chain.name}, '
                f'minimum required: 0.0001 $ETH.')
    else:
        logger.info(f"#{index} | {account.address}: "
                    f"already deployed {len(deployed_contracts.items)} contracts, limit exceeded.")

    if deployed_contracts and deployed_contracts.items:
        for item in deployed_contracts.items:
            append_to_file_if_not_exists(
                file_path=rhino_contracts_path,
                string=f"app.rhino.fi/realm/trackers/TAIKO/deploy-and-interact/friend?contractAddress={item.id.address}"
            )
