from datetime import datetime

from loguru import logger

from datatypes.account import AccountItem
from sdk.sql import SQL
from settings.constants import database_path, private_keys_path
from tools.add_logger import add_logger
from tools.other_utils import read_file


def add_accs_to_db(sql: SQL, accs_path: str, tier: str, owner: str):
    lines = read_file(accs_path)

    for line in lines:
        if '##' in line:
            private_key, proxy = line.split('##')
        else:
            private_key = line
            proxy = ''

        acc = AccountItem(
            private_key=private_key,
            proxy=proxy,
            owner=owner,
            tier=tier,
            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        result = sql.add_acc(acc=acc)
        if result:
            logger.info(f'new wallet: {private_key} with proxy [{acc.proxy}] and owner [{acc.owner}].')
        else:
            logger.info(f'wallet: {private_key} with owner [{acc.owner}] is already in the db.')


if __name__ == '__main__':
    add_logger()
    try:
        sql = SQL(database=database_path)
        owner = input('owner: ')
        tier = input('tier (A, B, C): ')
        add_accs_to_db(sql=sql, owner=owner, tier=tier, accs_path=private_keys_path)
    except Exception as e:
        logger.exception(e)
