import random

from loguru import logger
from web3 import Web3

from datatypes.account import AccountItem
from sdk.sql import SQL
from tools.other_utils import sleep_in_range
from tools.trailblazers import update_trailblazers_profile
from user_data.config import sleep_between_txs_in_sec, leaderboard_update_on_every_module_start


def execute_task(
        sql: SQL,
        acc: AccountItem,
        task_func,
        task_range: (int, int),
        today: str,
        start_sleep: bool = True,
        ignore_sleep_after: bool = False
):
    if start_sleep:
        sleep_in_range(sleep_between_txs_in_sec[0], sleep_between_txs_in_sec[1])

    acc.address = Web3().eth.account.from_key(acc.private_key).address

    loop_count = random.randint(task_range[0], task_range[1])
    if loop_count > 1:
        if leaderboard_update_on_every_module_start:
            update_trailblazers_profile(sql=sql, account=acc)
        for i in range(loop_count):
            try:
                task_func(sql, acc, today)
                if not ignore_sleep_after:
                    sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])
            except Exception as e:
                logger.exception(e)
    elif loop_count == 1:
        if leaderboard_update_on_every_module_start:
            update_trailblazers_profile(sql=sql, account=acc)
        try:
            task_func(sql, acc, today)
            if not ignore_sleep_after:
                sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])
        except Exception as e:
            logger.exception(e)
