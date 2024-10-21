from loguru import logger

from data.constants import database_path, version
from executors.week import main_week_executor
from sdk.sql import SQL
from tools.add_logger import add_logger
from tools.other_utils import sleep_in_range
from user_data.config import sleep_after_loop_in_sec

if __name__ == '__main__':
    add_logger(version=version)
    try:
        sql = SQL(database_path=database_path)
        while True:
            try:
                main_week_executor(sql=sql, badge_id=7)
                main_week_executor(sql=sql, badge_id=8)

                sleep_in_range(
                    sec_from=sleep_after_loop_in_sec[0],
                    sec_to=sleep_after_loop_in_sec[1],
                    log='after loop finish'
                )
            except Exception as e:
                logger.exception(e)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
