import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from web3 import Web3

from data.constants import taiko_weth_contract, taiko_token, hana_eth_token, meridian_eth_token
from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.crypto import get_balance, get_balance_of
from tools.sql import sql_get_accs, sql_add_burners
from user_data.chains import taiko_chain, source_chains, destination_chains
from user_data.config import workers_range


def balance_checker_single_executor(acc: AccountItem, sql: SQL):
    total_balance = 0
    burner_account = Web3().eth.account.from_key(sql.get_burner_by_id(acc_id=acc.id))

    main_balance = get_balance(address=acc.address, rpc=taiko_chain.rpc)
    total_balance += main_balance.float

    balance = f'#{acc.id}: {acc.address}: {main_balance.float} $ETH, '

    unique_chains = list(set(source_chains + destination_chains))
    for chain in unique_chains:
        chain_balance = get_balance(address=acc.address, rpc=chain.rpc)
        if chain_balance.float > 0.0001:
            total_balance += chain_balance.float
            balance += f'{chain_balance.float} $ETH [{chain.name}], '

    warning = False

    main_weth_balance = get_balance_of(address=acc.address, contract=taiko_weth_contract)
    if main_weth_balance.float > 0.0001:
        warning = True
        total_balance += main_weth_balance.float
    balance += f'{main_weth_balance.float} $wETH, '

    main_taiko_balance = get_balance_of(address=acc.address, contract=taiko_token.address)
    if main_taiko_balance.float > 0.0001:
        warning = True
    balance += f'{main_taiko_balance.float} $TAIKO, '

    meridian_supplied_eth_balance = get_balance_of(address=acc.address, contract=meridian_eth_token.address)
    if meridian_supplied_eth_balance.float > 0.0001:
        total_balance += meridian_supplied_eth_balance.float
        warning = True
        balance += f'{meridian_supplied_eth_balance.float} $mETH, '

    hana_supplied_eth_balance = get_balance_of(address=acc.address, contract=hana_eth_token.address)
    if hana_supplied_eth_balance.float > 0.0001:
        total_balance += hana_supplied_eth_balance.float
        warning = True
        balance += f'{hana_supplied_eth_balance.float} $aETH, '

    burner_balance = get_balance(address=burner_account.address, rpc=taiko_chain.rpc)
    if burner_balance.float > 0.0001:
        total_balance += burner_balance.float
        balance += f'{burner_account.address}: {burner_balance.float} $ETH. '
        warning = True

    balance = f'{balance[:-2]} | total: {round(total_balance, 4)} $ETH.'
    if warning:
        logger.warning(balance)
    else:
        logger.info(balance)

    return total_balance


def balance_checker_executor(sql: SQL, accs: [AccountItem]):
    total_balance = 0

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(balance_checker_single_executor, acc, sql) for acc in accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                balance = future.result()
                total_balance += balance
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.info(f'total balance: {round(total_balance, 5)} $ETH.')


def main_balance_checker(sql: SQL, owner: str = ''):
    total_accs = sql_get_accs(sql=sql, owner=owner)
    sql_add_burners(sql=sql, accs=total_accs)
    balance_checker_executor(sql=sql, accs=total_accs)
