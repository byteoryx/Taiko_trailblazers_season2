from loguru import logger

from data.constants import database_path, version
from executors.badge_parser import conft_parser_executor
from sdk.sql import SQL
from tools.add_logger import add_logger

if __name__ == '__main__':
    add_logger(version=version)
    try:
        sql = SQL(database_path=database_path)
        conft_parser_executor(sql=sql)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
    except Exception as e:
        logger.exception(e)
