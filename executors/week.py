import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from loguru import logger

from datatypes.account import AccountItem
from executors.task import execute_task
from modules.week import week_main
from sdk.sql import SQL
from tools.other_utils import sleep_in_range, get_today_table_name
from tools.sql import sql_get_accs, sql_get_not_minted_badge
from tools.task import brigade_nft_task, crack_x_stack_task, meridian_usdc_task, meridian_usdc_withdraw_task
from user_data.config import shuffle_accounts, workers_range
from user_data.config import sleep_between_txs_in_sec


def main_week8_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    logger.info(f'#{acc.id} | {acc.address}: week8 start.')
    result = week_main(
        index=acc.id,
        private_key=acc.private_key,
        sql=sql,
        day=today_bridge,
        badge_id=7,
        proxy=acc.proxy
    )
    if result:
        if 'not whitelisted' in result:
            tasks = [
                {"task_func": meridian_usdc_task, "task_range": (1, 1), "log_suffix": 'meridian'}
            ]

            random.shuffle(tasks)

            for task in tasks:
                if task["task_range"] != (0, 0):
                    execute_task(
                        sql, acc, task["task_func"], task["task_range"],
                        today_bridge, True, False
                    )

            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
            week_main(
                index=acc.id,
                private_key=acc.private_key,
                sql=sql,
                day=today_bridge,
                badge_id=7,
                proxy=acc.proxy
            )

    execute_task(sql, acc, meridian_usdc_withdraw_task, (1, 1), today_bridge)
    logger.info(f'#{acc.id} | {acc.address}: week8 finish.')


def main_week7_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    logger.info(f'#{acc.id} | {acc.address}: week7 start.')
    result = week_main(
        index=acc.id,
        private_key=acc.private_key,
        sql=sql,
        day=today_bridge,
        badge_id=6,
        proxy=acc.proxy
    )
    if result:
        if 'not whitelisted' in result:
            tasks = [
                {"task_func": brigade_nft_task, "task_range": (0, 1), "log_suffix": 'brigade nft'},
                {"task_func": crack_x_stack_task, "task_range": (0, 1), "log_suffix": 'crack-&-stack'}
            ]

            random.shuffle(tasks)

            for task in tasks:
                if task["task_range"] != (0, 0):
                    execute_task(
                        sql, acc, task["task_func"], task["task_range"],
                        today_bridge, True, False
                    )

            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
            week_main(
                index=acc.id,
                private_key=acc.private_key,
                sql=sql,
                day=today_bridge,
                badge_id=6,
                proxy=acc.proxy
            )
    logger.info(f'#{acc.id} | {acc.address}: week7 finish.')


def taiko_week8_main_executor(sql: SQL, accs: [AccountItem], today_bridge: str, total_accs_len: int):
    if accs:
        logger.info(f'{len(accs)}/{total_accs_len} to be used for week8.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_week8_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(accs)} accs have been processed with week8.')

    else:
        logger.success(f'every acc is processed with week8.')


def taiko_week7_main_executor(sql: SQL, accs: [AccountItem], today_bridge: str, total_accs_len: int):
    if accs:
        logger.info(f'{len(accs)}/{total_accs_len} to be used for week7.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_week7_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(accs)} accs have been processed with week7.')

    else:
        logger.success(f'every acc is processed with week7.')


def main_week_executor(sql: SQL, badge_id: int):
    today = datetime.now(timezone.utc).strftime("%B%d")
    today_bridge = get_today_table_name()

    sql.create_report_day_table(today_bridge)
    sql.create_badge_table(badge_id=badge_id)

    total_accs = sql_get_accs(sql=sql)
    accs = sql_get_not_minted_badge(sql=sql, badge_id=badge_id, total_accs=total_accs)
    if accs:
        if shuffle_accounts:
            random.shuffle(accs)

        if badge_id == 7:
            taiko_week7_main_executor(
                sql=sql,
                accs=accs,
                today_bridge=today_bridge,
                total_accs_len=len(total_accs)
            )
        if badge_id == 8:
            taiko_week8_main_executor(
                sql=sql,
                accs=accs,
                today_bridge=today_bridge,
                total_accs_len=len(total_accs)
            )
    else:
        logger.success(f'every acc is processed with week{badge_id}_task.')
