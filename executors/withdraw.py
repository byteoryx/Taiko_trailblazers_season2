import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from datatypes.account import AccountItem
from executors.task import execute_task
from sdk.sql import SQL
from tools.task import bridge_withdraw, unwrap_task, burner_withdraw_task, hana_withdraw_task, meridian_withdraw_task
from user_data.config import workers_range


def main_single_withdraw_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    tasks = [
        (burner_withdraw_task, (1, 1)),
        (unwrap_task, (1, 1)),
        (hana_withdraw_task, (1, 1)),
        (meridian_withdraw_task, (1, 1)),
    ]

    random.shuffle(tasks)

    for task, args in tasks:
        execute_task(sql, acc, task, args, today_bridge)


def collect_stuck_balance_executor(sql: SQL, today_bridge: str, total_accs: [AccountItem]):
    logger.success(f'{len(total_accs)} accs to be used for withdraw_taiko.')

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(main_single_withdraw_executor, acc, sql, today_bridge) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{len(total_accs)} accs have been processed with taiko_withdraw.\n')


def main_single_withdraw_from_taiko_to_recipient_chains_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    if acc.config.common.withdraw_from_taiko_to_recipients_chains:
        execute_task(sql, acc, bridge_withdraw, (1, 1), today_bridge)
    else:
        logger.info(f"#{acc.id} | {acc.address}: "
                    f"bridge from taiko to recipient_chains is disabled for [tier-{acc.tier}].")


def withdraw_from_taiko_to_recipient_chains_executor(sql: SQL, today_bridge: str, total_accs: [AccountItem]):
    logger.success(f'{len(total_accs)} accs to be used for bridge_taiko_to_recipients.')

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(
            main_single_withdraw_from_taiko_to_recipient_chains_executor, acc, sql, today_bridge
        ) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{len(total_accs)} accs have been processed with bridge_taiko_to_recipients.\n')
