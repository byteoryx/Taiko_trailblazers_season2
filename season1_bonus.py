from loguru import logger

from data.constants import database_path, version
from executors.season1_bonus import main_season1_bonus
from sdk.sql import SQL
from tools.add_logger import add_logger

if __name__ == '__main__':
    add_logger(version=version)
    try:
        sql = SQL(database_path=database_path)
        main_season1_bonus(sql=sql)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
