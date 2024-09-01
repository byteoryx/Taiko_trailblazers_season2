from loguru import logger

from sdk.sql import SQL
from settings.constants import database_path, version
from tools.add_logger import add_logger
from tools.executor import main_balance_checker

if __name__ == '__main__':
    add_logger(version=version)
    sql = SQL(database_path)

    try:
        main_balance_checker(sql=sql)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
