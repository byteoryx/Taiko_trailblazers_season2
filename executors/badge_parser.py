import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.conft_parser import get_owned_badges
from tools.sql import sql_get_accs
from user_data.config import workers_range


def conft_parser_single_executor(acc: AccountItem, sql: SQL):
    badges, count = get_owned_badges(
        address=acc.address.lower(),
        private_key=acc.private_key,
        id=acc.id,
        sql=sql,
        proxy=acc.proxy
    )
    if badges:
        status = sql.update_badges(acc=acc, badges=badges, count=count)
        if status:
            logger.info(f'#{acc.id} | {acc.address} | {count}: {status}.')
        else:
            logger.info(f'#{acc.id} | {acc.address} | {count}: {badges}.')
    else:
        logger.info(f'#{acc.id} | {acc.address} | no owned badges.')


def conft_parser_executor(sql: SQL):
    total_accs = sql_get_accs(sql=sql)

    logger.success(f'{len(total_accs)} accs to be used for badge_parser.')

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(conft_parser_single_executor, acc, sql) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{len(total_accs)} accs have been processed with badge_parser.')
