from loguru import logger

from sdk.sql import SQL
from settings.constants import database_path, version
from tools.add_logger import add_logger
from tools.executor import conft_parser_executor

if __name__ == '__main__':
    add_logger(version=version)
    sql = SQL(database_path)

    try:
        conft_parser_executor(sql=sql)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
    except Exception as e:
        logger.exception(e)
