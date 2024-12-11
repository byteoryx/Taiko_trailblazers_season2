import random

from loguru import logger

from data.constants import version, database_path
from executors.withdraw import collect_stuck_balance_executor
from sdk.sql import SQL
from tools.add_logger import add_logger
from tools.other_utils import get_today_table_name, insert_tier_configs_into_account_items, sleep_in_range
from tools.sql import sql_add_burners, sql_get_accs
from user_data.config import shuffle_accounts, sleep_after_loop_in_sec

if __name__ == '__main__':
    add_logger(version=version)
    sql = SQL(database_path=database_path)

    today_table_name = get_today_table_name()
    total_accs = insert_tier_configs_into_account_items(accounts=sql_get_accs(sql=sql))
    sql_add_burners(sql=sql, accs=total_accs)

    while True:
        try:
            sql.create_report_day_table(day=today_table_name)

            if shuffle_accounts:
                random.shuffle(total_accs)

            collect_stuck_balance_executor(
                sql=sql, today_bridge=today_table_name, total_accs=total_accs
            )

            logger.info(f"withdraw stuck balance on taiko is completed.")

            sleep_in_range(
                sec_from=sleep_after_loop_in_sec[0],
                sec_to=sleep_after_loop_in_sec[1],
                log="after loop finish"
            )
        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            logger.success('exited by user.')
            exit()
