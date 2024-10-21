import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone, datetime

from loguru import logger
from web3 import Web3

from datatypes.account import AccountItem
from modules.transfer import transfer_main
from sdk.sql import SQL
from tools.crypto import get_balance
from tools.other_utils import get_leave_on_source
from user_data.chains import destination_chains
from user_data.config import shuffle_accounts, workers_range, minimum_transfer


def single_cex_collector_executor(acc: AccountItem, sql, today):
    address = Web3().eth.account.from_key(acc.private_key).address

    at_least_one_transfer = False
    random.shuffle(destination_chains)

    for chain in destination_chains:
        balance = get_balance(address=address, rpc=chain.rpc)

        leave_on_source = get_leave_on_source(tier=acc.tier, chain=chain.name)

        if balance.float > leave_on_source + minimum_transfer:
            at_least_one_transfer = True
            transfer_amount = balance.float - round(leave_on_source * random.uniform(1, 1.1), random.randint(5, 8))
            transfer_main(
                index=acc.id,
                private_key=acc.private_key,
                address=acc.cex_address,
                sql=sql,
                day=today,
                transfer_amount=transfer_amount,
                chain=chain
            )

    if not at_least_one_transfer:
        logger.warning(f'#{acc.id} | {address}: nothing to deposit on cex.')


def main_cex_collector_executor(total_accs: [AccountItem], sql: SQL):
    today = datetime.now(timezone.utc).strftime("%B%d")
    if total_accs:
        if shuffle_accounts:
            random.shuffle(total_accs)

        logger.success(f'{len(total_accs)} accs to be used for taiko_cex_collector.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(single_cex_collector_executor, acc, sql, today) for acc in total_accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(total_accs)} accs have been processed with taiko_cex_collector.\n')

    else:
        logger.success(f'taiko_cex_collector | no accounts to withdraw from.\n')
