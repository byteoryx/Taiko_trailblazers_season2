from loguru import logger

from data.constants import version, database_path
from executors.main import main_taiko
from sdk.sql import SQL
from tools.add_logger import add_logger
from user_data.config import leaderboard_update_on_script_start

if __name__ == '__main__':
    add_logger(version=version)
    sql = SQL(database_path=database_path)

    while True:
        try:
            main_taiko(
                sql=sql,
                leaderboard_update=leaderboard_update_on_script_start
            )
        except Exception as e:
            logger.exception(e)
        except KeyboardInterrupt:
            logger.success('exited by user.')
            exit()
