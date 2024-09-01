import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from loguru import logger
from web3 import Web3

from datatypes.account import AccountItem
from modules.collector import main_collector_executor
from modules.transfer import burner_transfer_main
from modules.week import week_main
from sdk.sql import SQL
from settings.chains import taiko_chain
from settings.config import shuffle_accounts, workers_range, withdraw_from_taiko_to_source_chains, \
    sleep_after_loop_in_sec, \
    deposit_from_source_chains_to_taiko, \
    wraps_range, conft_mint_range, omnihub_mint_range, rubyscore_votes_range, rhino_gms_range, self_transfer_range, \
    brigade_nft_claim, minimum_taiko_balance, burner_transfer_range, crack_x_stack_range, \
    zypher2048_range
from settings.config import sleep_between_txs_in_sec
from settings.constants import taiko_weth_contract
from tools.conft_parser import get_owned_badges
from tools.crypto import get_balance, get_balance_of
from tools.other_utils import sleep_in_range, get_today_bridge
from tools.sql import sql_get_accs, sql_get_accs_to_work, sql_get_accs_to_deposit, sql_add_burners, \
    sql_get_not_minted_badge
from tools.task import bridge_withdraw, bridge_deposit, brigade_nft_task, self_transfer_task, rhino_task, \
    rubyscore_task, omnihub_task, conft_task, wrap_task, burner_transfer_task, crack_x_stack_task, zypher2048_task, \
    unwrap_task, burner_withdraw_task, meridian_task, kiloex_task
from tools.trailblazers import update_trailblazers_profile


def execute_task(sql: SQL, acc: AccountItem, task_func, task_range: (int, int),
                 today: str, log_suffix: str,
                 start_sleep: bool = True,
                 ignore_sleep_after: bool = False,
                 update_leaderboard: bool = True):
    if start_sleep:
        sleep_in_range(sleep_between_txs_in_sec[0], sleep_between_txs_in_sec[1])

    acc.address = Web3().eth.account.from_key(acc.private_key).address

    loop_count = random.randint(task_range[0], task_range[1])
    if loop_count > 1:
        if update_leaderboard:
            update_trailblazers_profile(sql=sql, account=acc)
        for i in range(loop_count):
            try:
                task_func(sql, acc, today)
                if not ignore_sleep_after:
                    sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])
            except Exception as e:
                logger.exception(e)
    elif loop_count == 1:
        if update_leaderboard:
            update_trailblazers_profile(sql=sql, account=acc)
        try:
            task_func(sql, acc, today)
            if not ignore_sleep_after:
                sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])
        except Exception as e:
            logger.exception(e)


def main_single_report_executor(acc: AccountItem, sql: SQL):
    update_trailblazers_profile(sql=sql, account=acc)
    sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])


def main_single_withdraw_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    execute_task(sql, acc, unwrap_task, (1, 1), today_bridge, 'unwrap')
    execute_task(sql, acc, burner_withdraw_task, (1, 1), today_bridge, 'burner-withdraw')
    if withdraw_from_taiko_to_source_chains:
        execute_task(sql, acc, bridge_withdraw, (1, 1), today_bridge, 'bridge withdraw')


def main_single_deposit_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    if deposit_from_source_chains_to_taiko:
        execute_task(sql, acc, bridge_deposit, (1, 1), today_bridge, 'bridge deposits')


def main_week8_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    logger.info(f'#{acc.id} | {acc.address}: week8 start.')
    result = week_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today_bridge, badge_id=7)
    if result:
        if 'not whitelisted' in result:
            tasks = [
                {"task_func": meridian_task, "task_range": (0, 1), "log_suffix": 'meridian'},
                {"task_func": kiloex_task, "task_range": (0, 1), "log_suffix": 'kiloex'},
            ]

            random.shuffle(tasks)

            for task in tasks:
                if task["task_range"] != (0, 0):
                    execute_task(
                        sql, acc, task["task_func"], task["task_range"],
                        today_bridge, task["log_suffix"], True, True, False
                    )

            week_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today_bridge, badge_id=7)
    logger.info(f'#{acc.id} | {acc.address}: week8 finish.')


def main_week7_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    logger.info(f'#{acc.id} | {acc.address}: week7 start.')
    result = week_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today_bridge, badge_id=6)
    if result:
        if 'not whitelisted' in result:
            tasks = [
                {"task_func": brigade_nft_task, "task_range": (0, 1), "log_suffix": 'brigade nft'},
                {"task_func": crack_x_stack_task, "task_range": (0, 1), "log_suffix": 'crack-&-stack'}
            ]

            random.shuffle(tasks)

            for task in tasks:
                if task["task_range"] != (0, 0):
                    execute_task(
                        sql, acc, task["task_func"], task["task_range"],
                        today_bridge, task["log_suffix"], True, False, False
                    )

            week_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today_bridge, badge_id=6)
    logger.info(f'#{acc.id} | {acc.address}: week7 finish.')


def burner_collector_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(
        index=acc.id, main_private_key=acc.private_key,
        burner_private_key=burner_key,
        sql=sql, day=today_bridge, multiplier_range=(1, 1), withdraw_only=True
    )


def main_single_executor(acc: AccountItem, sql: SQL, today_bridge: str):
    logger.info(f'#{acc.id} | {acc.address}: main_taiko start.')

    tasks = [
        {"task_func": wrap_task, "task_range": wraps_range, "log_suffix": 'wraps'},
        {"task_func": conft_task, "task_range": conft_mint_range, "log_suffix": 'conft mint'},
        {"task_func": omnihub_task, "task_range": omnihub_mint_range, "log_suffix": 'omnihub mint'},
        {"task_func": rubyscore_task, "task_range": rubyscore_votes_range, "log_suffix": 'rubyscore vote'},
        {"task_func": rhino_task, "task_range": rhino_gms_range, "log_suffix": 'rhino gm'},
        {"task_func": self_transfer_task, "task_range": self_transfer_range, "log_suffix": 'self-transfer'},
        {"task_func": burner_transfer_task, "task_range": burner_transfer_range, "log_suffix": 'burner-transfer'},
        {"task_func": brigade_nft_task, "task_range": (1, 1) if brigade_nft_claim else (0, 0),
         "log_suffix": 'brigade nft'},
        {"task_func": crack_x_stack_task, "task_range": crack_x_stack_range, "log_suffix": 'crack-&-stack'},
        {"task_func": zypher2048_task, "task_range": zypher2048_range, "log_suffix": 'zypher2048'}
    ]

    random.shuffle(tasks)

    for task in tasks:
        if task["task_range"] != (0, 0):
            execute_task(sql, acc, task["task_func"], task["task_range"], today_bridge, task["log_suffix"])

    if withdraw_from_taiko_to_source_chains:
        execute_task(sql, acc, bridge_withdraw, (1, 1), today_bridge, 'bridge withdraw')

    logger.info(f'#{acc.id} | {acc.address}: main_taiko finish.')


def leaderboard_update_executor(today: str, total_accs: [AccountItem], sql: SQL):
    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs to be used for trailblazers_report.')
    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(main_single_report_executor, acc, sql) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs have been processed with trailblazers_report.')


def deposit_executor(sql: SQL, today: str, today_bridge: str):
    deposit_accs = sql_get_accs_to_deposit(sql=sql, day=today_bridge, shuffle=shuffle_accounts)
    if deposit_accs:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(deposit_accs)} accs to be used for deposit_taiko.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_single_deposit_executor, acc, sql, today_bridge) for acc in deposit_accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(deposit_accs)} accs have been processed with deposit_taiko.')
    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(deposit_accs)} accs have been processed with deposit_taiko.')


def taiko_main_executor(sql: SQL, today_bridge: str, today: str):
    accs = sql_get_accs_to_work(sql=sql, day=today_bridge,
                                shuffle=shuffle_accounts, minimum_required_balance=minimum_taiko_balance)
    if accs:
        logger.info(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                    f'{len(accs)} to be used for taiko_main.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs have been processed with taiko_main.')

    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with taiko_main.')


def withdraw_executor(sql: SQL, today: str, today_bridge: str, total_accs: [AccountItem]):
    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs to be used for withdraw_taiko.')

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(main_single_withdraw_executor, acc, sql, today_bridge) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs have been processed with taiko_withdraw.')


def conft_parser_single_executor(acc: AccountItem, sql: SQL):
    badges, count = get_owned_badges(address=acc.address.lower(), private_key=acc.private_key, id=acc.id, sql=sql)
    if badges:
        status = sql.update_badges(acc=acc, badges=badges, count=count)
        if status:
            logger.info(f'#{acc.id} | {acc.address} | {count}: {status}.')
        else:
            logger.info(f'#{acc.id} | {acc.address} | {count}: {badges}.')
    else:
        logger.info(f'#{acc.id} | {acc.address} | no owned badges.')


def conft_parser_executor(sql: SQL):
    today = datetime.now(timezone.utc).strftime("%B%d")
    total_accs = sql_get_accs(sql=sql)

    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs to be used for badge_parser.')

    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(conft_parser_single_executor, acc, sql) for acc in total_accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")

    logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                   f'{len(total_accs)} accs have been processed with badge_parser.')


def main_taiko(sql: SQL, collector_acc_path: str, sleep_after_loop: bool = True, leaderboard_update: bool = True):
    today = datetime.now(timezone.utc).strftime("%B%d")
    today_bridge = get_today_bridge()

    total_accs = sql_get_accs(sql=sql)

    sql.create_bridge_day_table(today_bridge)
    sql_add_burners(sql=sql, accs=total_accs)

    if shuffle_accounts:
        random.shuffle(total_accs)

    if leaderboard_update:
        leaderboard_update_executor(sql=sql, today=today, total_accs=total_accs)

    if deposit_from_source_chains_to_taiko:
        deposit_executor(sql=sql, today=today, today_bridge=today_bridge)

    taiko_main_executor(sql=sql, today_bridge=today_bridge, today=today)
    main_burner_collector(sql=sql)

    withdraw_executor(sql=sql, today_bridge=today_bridge, today=today, total_accs=total_accs)
    if withdraw_from_taiko_to_source_chains:
        main_collector_executor(acc_path=collector_acc_path, sql=sql)

    if sleep_after_loop:
        sleep_in_range(sec_from=sleep_after_loop_in_sec[0], sec_to=sleep_after_loop_in_sec[1], log='after loop finish')


def taiko_week8_main_executor(sql: SQL, accs: [AccountItem], today_bridge: str, today: str, total_accs_len: int):
    if accs:
        logger.info(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                    f'{len(accs)}/{total_accs_len} to be used for week8.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_week8_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs have been processed with week8.')

    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with week8.')


def taiko_week7_main_executor(sql: SQL, accs: [AccountItem], today_bridge: str, today: str, total_accs_len: int):
    if accs:
        logger.info(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                    f'{len(accs)}/{total_accs_len} to be used for week7.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_week7_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs have been processed with week7.')

    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with week7.')


def main_week_executor(sql: SQL, badge_id: int):
    today = datetime.now(timezone.utc).strftime("%B%d")
    today_bridge = get_today_bridge()

    sql.create_bridge_day_table(today_bridge)
    sql.create_badge_table(badge_id=badge_id)

    total_accs = sql_get_accs(sql=sql)
    accs = sql_get_not_minted_badge(sql=sql, badge_id=badge_id, total_accs=total_accs)
    if accs:
        if shuffle_accounts:
            random.shuffle(accs)

        if badge_id == 7:
            taiko_week7_main_executor(sql=sql, accs=accs, today_bridge=today_bridge,
                                      today=today, total_accs_len=len(total_accs))
        if badge_id == 8:
            taiko_week8_main_executor(sql=sql, accs=accs, today_bridge=today_bridge,
                                      today=today, total_accs_len=len(total_accs))
    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with week_task.')


def collector_executor(sql: SQL, accs: [AccountItem], today_bridge: str, today: str):
    if accs:
        logger.info(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                    f'{len(accs)} to be used for burner_collector.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(burner_collector_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'{len(accs)} accs have been processed with burner_collector.')

    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with burner_collector.')


def main_burner_collector(sql: SQL):
    today = datetime.now(timezone.utc).strftime("%B%d")
    today_bridge = get_today_bridge()

    sql.create_bridge_day_table(today_bridge)

    total_accs = sql_get_accs(sql=sql)
    if total_accs:
        if shuffle_accounts:
            random.shuffle(total_accs)

        collector_executor(sql=sql, accs=total_accs, today_bridge=today_bridge, today=today)

    else:
        logger.success(f'{today} [{datetime.now(timezone.utc).strftime("%H:%M:%S")}] | '
                       f'every acc is processed with burner_collector.')


def balance_checker_single_executor(acc: AccountItem, sql: SQL):
    burner_account = Web3().eth.account.from_key(sql.get_burner_by_id(acc_id=acc.id))
    burner_balance = get_balance(address=burner_account.address, rpc=taiko_chain.rpc)
    main_balance = get_balance(address=acc.address, rpc=taiko_chain.rpc)
    main_weth_balance = get_balance_of(address=acc.address, contract=taiko_weth_contract)

    warning = False
    balance = f'#{acc.id}: {acc.address}: {main_balance.float} $ETH, '
    if main_weth_balance.int:
        if main_weth_balance.float > 0.0001:
            warning = True
        balance += f'{main_weth_balance.float} $wETH, '

    balance += f'{burner_account.address}: {burner_balance.float} $ETH.'
    if burner_balance.float > 0.0001:
        warning = True

    if warning:
        logger.warning(balance)
    else:
        logger.info(balance)


def balance_checker_executor(sql: SQL, accs: [AccountItem]):
    with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
        futures = [executor.submit(balance_checker_single_executor, acc, sql) for acc in accs]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred during processing: {e}")


def main_balance_checker(sql: SQL):
    total_accs = sql_get_accs(sql=sql)
    sql_add_burners(sql=sql, accs=total_accs)
    balance_checker_executor(sql=sql, accs=total_accs)
