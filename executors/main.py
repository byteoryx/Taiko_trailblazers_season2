import concurrent.futures
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from loguru import logger

from datatypes.account import AccountItem, DayBridgeItem
from executors.deposit import deposit_executor
from executors.report import leaderboard_update_executor
from executors.task import execute_task
from executors.withdraw import withdraw_executor
from modules.collector import main_cex_collector_executor
from sdk.sql import SQL
from tools.crypto import get_account_nonce
from tools.other_utils import sleep_in_range, get_today_table_name
from tools.sql import sql_get_accs, sql_get_accs_to_work, sql_add_burners
from tools.task import (
    brigade_nft_task,
    self_transfer_task,
    rhino_task,
    rubyscore_task,
    omnihub_task,
    conft_task,
    wrap_task,
    burner_transfer_task,
    crack_x_stack_task,
    zypher2048_task,
    taikodrips_task,
    oxastra_task,
    contract_task
)
from user_data.config import (
    shuffle_accounts,
    workers_range,
    withdraw_from_taiko_to_source_chains,
    sleep_after_loop_in_sec,
    deposit_from_source_chains_to_taiko,
    wraps_range,
    conft_mint_range,
    omnihub_mint_range,
    rubyscore_votes_range,
    rhino_gms_range,
    self_transfer_range,
    brigade_game,
    minimum_taiko_balance,
    burner_transfer_range,
    crack_x_stack_range,
    zypher2048_range,
    taikodrips_stake,
    oxastra_boost,
    contract_deploy_range
)


def main_single_executor(acc: AccountItem, sql: SQL, today_table_name: str):
    old_account_nonce = get_account_nonce(private_key=acc.private_key)

    tasks = [
        {"task_func": wrap_task, "task_range": wraps_range, "log_suffix": 'wraps'},
        {"task_func": conft_task, "task_range": conft_mint_range, "log_suffix": 'conft mint'},
        {"task_func": omnihub_task, "task_range": omnihub_mint_range, "log_suffix": 'omnihub mint'},
        {"task_func": rubyscore_task, "task_range": rubyscore_votes_range, "log_suffix": 'rubyscore vote'},
        {"task_func": rhino_task, "task_range": rhino_gms_range, "log_suffix": 'rhino gm'},
        {"task_func": self_transfer_task, "task_range": self_transfer_range, "log_suffix": 'self-transfer'},
        {"task_func": burner_transfer_task, "task_range": burner_transfer_range, "log_suffix": 'burner-transfer'},
        {"task_func": brigade_nft_task, "task_range": (1, 1) if brigade_game else (0, 0),
         "log_suffix": 'brigade nft'},
        {"task_func": crack_x_stack_task, "task_range": crack_x_stack_range, "log_suffix": 'crack-&-stack'},
        {"task_func": zypher2048_task, "task_range": zypher2048_range, "log_suffix": 'zypher2048'},
        {"task_func": taikodrips_task, "task_range": (1, 1) if taikodrips_stake else (0, 0),
         "log_suffix": 'taikodrips'},
        {"task_func": oxastra_task, "task_range": (1, 1) if oxastra_boost else (0, 0), "log_suffix": '0xAstra'},
        {"task_func": contract_task, "task_range": contract_deploy_range, "log_suffix": 'contract deploy'},
    ]

    random.shuffle(tasks)

    for task in tasks:
        if task["task_range"] != (0, 0):
            execute_task(sql, acc, task["task_func"], task["task_range"], today_table_name, task["log_suffix"])

    new_account_nonce = get_account_nonce(private_key=acc.private_key)
    new_txs = new_account_nonce - old_account_nonce

    volume, txs, costs = sql.get_volume_and_txs_by_id(day=today_table_name, acc_id=acc.id)
    status = sql.add_day_report(
        day_item=DayBridgeItem(
            id=acc.id,
            txs=txs + new_txs,
            volume=volume,
            costs=costs,
            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        day=today_table_name,
        acc_id=acc.id
    )

    if status:
        logger.info(f"#{acc.id} | {acc.address}: {status}.")


def taiko_main_executor(sql: SQL, today_bridge: str):
    logger.success(f'parsing accounts to be used with taiko_main by limits, tiers and existing balance.')
    accs = sql_get_accs_to_work(
        sql=sql,
        day=today_bridge,
        shuffle=shuffle_accounts,
        minimum_required_balance=minimum_taiko_balance
    )
    logger.success(f'accounts to be used with taiko_main have been parsed and collected.\n')
    if accs:
        logger.success(f'{len(accs)} accs to be used for taiko_main.')

        with ThreadPoolExecutor(max_workers=random.randint(workers_range[0], workers_range[1])) as executor:
            futures = [executor.submit(main_single_executor, acc, sql, today_bridge) for acc in accs]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f"Exception occurred during processing: {e}")

        logger.success(f'{len(accs)} accs have been processed with taiko_main.\n')

    else:
        logger.success(f'every acc is processed with taiko_main.\n')


def main_taiko(sql: SQL, sleep_after_loop: bool = True, leaderboard_update: bool = True):
    today_table_name = get_today_table_name()

    total_accs = sql_get_accs(sql=sql)

    sql.create_report_day_table(day=today_table_name)
    sql_add_burners(sql=sql, accs=total_accs)

    if shuffle_accounts:
        random.shuffle(total_accs)

    if leaderboard_update:
        leaderboard_update_executor(sql=sql, total_accs=total_accs)

    if deposit_from_source_chains_to_taiko:
        deposit_executor(sql=sql, today_bridge=today_table_name)

    taiko_main_executor(sql=sql, today_bridge=today_table_name)

    withdraw_executor(sql=sql, today_bridge=today_table_name, total_accs=total_accs)
    if withdraw_from_taiko_to_source_chains:
        main_cex_collector_executor(sql=sql, total_accs=total_accs)

    if sleep_after_loop:
        sleep_in_range(sec_from=sleep_after_loop_in_sec[0], sec_to=sleep_after_loop_in_sec[1], log='after loop finish')
