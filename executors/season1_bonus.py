import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.crypto import season1_bonus_claim_tx
from tools.sql import sql_get_accs, sql_add_burners
from user_data.chains import taiko_chain
from user_data.config import workers_range, shuffle_accounts


def season1_bonus_claim_single_executor(acc: AccountItem):
    tx_hash = season1_bonus_claim_tx(private_key=acc.private_key)
    if tx_hash:
        if "already registered" in tx_hash:
            logger.info(f'#{acc.id} | {acc.address}: season1_bonus already claimed.')
        else:
            logger.info(f'#{acc.id} | {acc.address}: season1_bonus | {taiko_chain.explorer}/{tx_hash}')
    else:
        logger.error(f'#{acc.id} | {acc.address}: season1_bonus tx has failed.')


def season1_bonus_claimer(accs: [AccountItem]):
    if accs:
        logger.info(f'{len(accs)} to be used for season1_bonus.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(season1_bonus_claim_single_executor, acc) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(accs)} accs have been processed with season1_bonus.')

    else:
        logger.success(f'every acc is processed with season1_bonus.')


def main_season1_bonus(sql: SQL, owner: str = ''):
    total_accs = sql_get_accs(sql=sql, owner=owner)
    if shuffle_accounts:
        random.shuffle(total_accs)
    sql_add_burners(sql=sql, accs=total_accs)
    season1_bonus_claimer(accs=total_accs)
