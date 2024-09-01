import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone, datetime

from loguru import logger
from web3 import Web3

from modules.transfer import transfer_main
from sdk.sql import SQL
from settings.chains import destination_chains
from settings.config import leave_on_source, shuffle_accounts, workers_range
from tools.crypto import get_balance
from tools.other_utils import get_csv_accs_pd


def single_collector_executor(acc, sql, today):
    address = Web3().eth.account.from_key(acc.private_key).address

    at_least_one_transfer = False
    random.shuffle(destination_chains)

    for chain in destination_chains:

        balance = get_balance(address=address, rpc=chain.rpc)
        if balance.float > leave_on_source + 0.001:
            at_least_one_transfer = False
            transfer_amount = balance.float - round(leave_on_source * random.uniform(1, 1.1), random.randint(5, 8))
            transfer_main(index=acc.id, private_key=acc.private_key, address=acc.cex_public,
                          sql=sql, day=today, transfer_amount=transfer_amount, chain=chain)
            logger.info(f'#{acc.id} | {address}: withdraw {round(transfer_amount, 6)} $ETH on [{chain.name}].')

    if not at_least_one_transfer:
        logger.warning(f'#{acc.id} | {address}: nothing to withdraw.')


def main_collector_executor(acc_path: str, sql: SQL):
    try:
        pd, accs = get_csv_accs_pd(path=acc_path)
    except:
        logger.error('add accounts into data/collector_accs.csv')
        return

    today = datetime.now(timezone.utc).strftime("%B%d")

    if shuffle_accounts:
        random.shuffle(accs)
    if accs:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs to be used for taiko_collector.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(single_collector_executor, acc, sql, today) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs have been processed with taiko_collector.')

    else:
        logger.success(f'taiko_collector | no accounts to withdraw from.')
