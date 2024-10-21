import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.other_utils import sleep_in_range
from tools.trailblazers import update_trailblazers_profile
from user_data.config import sleep_between_txs_in_sec, workers_range


def main_single_report_executor(acc: AccountItem, sql: SQL):
    update_trailblazers_profile(sql=sql, account=acc)
    sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])


def leaderboard_update_executor(total_accs: [AccountItem], sql: SQL):
    logger.success(f'{len(total_accs)} accs to be used for trailblazers_report.')
    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(main_single_report_executor, acc, sql) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{len(total_accs)} accs have been processed with trailblazers_report.\n')
