import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from datatypes.account import AccountItem
from executors.task import execute_task
from sdk.sql import SQL
from tools.sql import sql_get_accs_to_deposit
from tools.task import bridge_deposit
from user_data.config import shuffle_accounts, workers_range, deposit_from_source_chains_to_taiko


def main_single_deposit_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    if deposit_from_source_chains_to_taiko:
        execute_task(sql, acc, bridge_deposit, (1, 1), today_bridge, 'bridge deposits')


def deposit_executor(sql: SQL, today_bridge: str):
    logger.success(f'parsing accounts that will be used for deposit_taiko.')
    deposit_accs = sql_get_accs_to_deposit(sql=sql, day=today_bridge, shuffle=shuffle_accounts)
    if deposit_accs:
        logger.success(f'{len(deposit_accs)} accs to be used for deposit_taiko.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_single_deposit_executor, acc, sql, today_bridge) for acc in deposit_accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(deposit_accs)} accs have been processed with deposit_taiko.\n')
    else:
        logger.success(f'{len(deposit_accs)} accs have been processed with deposit_taiko.\n')
