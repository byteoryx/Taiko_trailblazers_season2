from loguru import logger

from sdk.sql import SQL
from settings.constants import database_path, version
from tools.add_logger import add_logger
from tools.executor import main_taiko

if __name__ == '__main__':
    add_logger(version=version)
    sql = SQL(database_path)

    try:
        while True:
            try:
                main_taiko(sql=sql, collector_acc_path='data/collector_accs.csv')
            except Exception as e:
                logger.exception(e)
    except KeyboardInterrupt:
        logger.success('exited by user.')
        exit()
