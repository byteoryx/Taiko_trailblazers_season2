import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from loguru import logger

from datatypes.account import AccountItem
from modules.transfer import burner_transfer_main
from sdk.sql import SQL
from tools.other_utils import get_today_table_name
from tools.sql import sql_get_accs
from user_data.config import shuffle_accounts, workers_range


def burner_collector_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(
        index=acc.id, main_private_key=acc.private_key,
        burner_private_key=burner_key,
        sql=sql, day=today_bridge, multiplier_range=(1, 1), withdraw_only=True
    )


def burner_collector_executor(sql: SQL, accs: [AccountItem], today_bridge: str, today: str):
    if accs:
        logger.success(f'{len(accs)} to be used for burner_collector.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(burner_collector_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(accs)} accs have been processed with burner_collector.\n')

    else:
        logger.success(f'every acc is processed with burner_collector.\n')


def main_burner_collector(sql: SQL):
    today = datetime.now(timezone.utc).strftime("%B%d")
    today_bridge = get_today_table_name()

    sql.create_report_day_table(today_bridge)

    total_accs = sql_get_accs(sql=sql)
    if total_accs:
        if shuffle_accounts:
            random.shuffle(total_accs)

        burner_collector_executor(sql=sql, accs=total_accs, today_bridge=today_bridge, today=today)

    else:
        logger.success(f'every acc is processed with burner_collector.\n')
