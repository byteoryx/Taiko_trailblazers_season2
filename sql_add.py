from datetime import datetime

from loguru import logger

from data.constants import database_path, private_keys_path
from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.add_logger import add_logger
from tools.other_utils import read_file


def add_accs_to_db(sql: SQL, accs_path: str, tier: str, owner: str):
    lines = read_file(accs_path)

    for index, line in enumerate(lines, start=1):
        parts = line.strip().split('##')

        private_key = parts[0]
        cex_address = None
        proxy = None

        if len(parts) == 3:
            _, cex_address, proxy = parts
        elif len(parts) == 2:
            if parts[1].startswith('0x'):
                cex_address = parts[1]
            else:
                proxy = parts[1]
        elif len(parts) == 1:
            pass

        acc = AccountItem(
            private_key=private_key,
            cex_address=cex_address,
            proxy=proxy,
            owner=owner,
            tier=tier,
            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        result = sql.add_acc(acc=acc)
        if result:
            logger.info(
                f'#{index} | [{private_key}] with cex_address [{cex_address}], '
                f'proxy [{proxy}] and owner [{owner}] has been added to the db.'
            )
        else:
            logger.info(f'#{index} | [{private_key}] is already in the db.')


if __name__ == '__main__':
    add_logger()
    try:
        sql = SQL(database_path=database_path)
        owner = input('owner: ')
        tier = input('tier (A, B, C): ')
        add_accs_to_db(sql=sql, owner=owner, tier=tier, accs_path=private_keys_path)
    except Exception as e:
        logger.exception(e)
