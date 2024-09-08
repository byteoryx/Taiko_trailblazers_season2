import random
from datetime import datetime
from typing import List

from loguru import logger
from web3 import Web3

from datatypes.account import AccountItem, BurnerItem, BadgeItem
from datatypes.crypto import Balance
from sdk.sql import SQL
from settings.chains import source_chains, taiko_chain
from settings.config import minimum_transfer
from settings.tiers import tier_collection
from tools.crypto import get_balance, generate_private_key
from tools.trailblazers import get_total_trailblazer_count


def sql_get_accs(sql: SQL, owner: str = '') -> List[AccountItem]:
    accs = []

    if owner:
        fetched_accs = sql.fetch_all_by_owner(table=sql.accs_table, owner=owner)
    else:
        fetched_accs = sql.fetch_all(table=sql.accs_table)

    for acc in fetched_accs:
        accs.append(
            AccountItem(
                id=acc[0],
                private_key=acc[1],
                proxy=acc[2],
                owner=acc[3],
                tier=acc[4],
                last_edited=acc[5],
                address=Web3().eth.account.from_key(acc[1]).address
            )
        )

    return accs


def sql_get_not_minted_badge(sql: SQL, badge_id: int, total_accs: [AccountItem]):
    accs = []
    fetched_accs: [BadgeItem] = sql.fetch_not_minted_badge(badge_id=badge_id)

    fetched_ids = {acc[0] for acc in fetched_accs}

    for acc in total_accs:
        if acc.id in fetched_ids:
            accs.append(
                AccountItem(
                    id=acc.id,
                    private_key=acc.private_key,
                    proxy=acc.proxy,
                    owner=acc.owner,
                    tier=acc.tier,
                    last_edited=acc.last_edited,
                    address=Web3().eth.account.from_key(acc.private_key).address
                )
            )

    return accs


def sql_get_accounts_with_zero_minted(sql: SQL, day_index: int) -> List[AccountItem]:
    accs = []
    fetched_accs = sql.fetch_accounts_with_zero_minted(day_index=day_index)

    for acc in fetched_accs:
        accs.append(
            AccountItem(
                id=acc[0],
                private_key=acc[1],
                proxy=acc[2],
                owner=acc[3],
                tier=acc[4],
                last_edited=acc[5]
            )
        )

    return accs


def sql_get_accs_to_work(sql: SQL,
                         day: str,
                         shuffle: bool = False,
                         minimum_required_balance: float = 0
                         ) -> List[AccountItem]:
    total_accs = sql_get_accs(sql=sql)
    total_trailblazers = get_total_trailblazer_count(address=total_accs[0].address)

    accs = []
    for acc in total_accs:
        if acc.tier:
            balance = get_balance(address=acc.address, rpc=taiko_chain.rpc)

            if minimum_required_balance and balance.float <= minimum_required_balance:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used because of low balance: '
                    f'{balance.float} $ETH on taiko, minimum required: {round(minimum_required_balance, 6)} $ETH.'
                )
                continue

            costs = sql.get_total_costs(acc_id=acc.id)
            today_txs = sql.get_today_txs(day=day, acc_id=acc.id)
            today_volume = sql.get_today_volume(day=day, acc_id=acc.id)
            rank = sql.get_rank(acc_id=acc.id)
            if rank:
                leaderboard_top = round(rank / total_trailblazers * 100, 2)
            else:
                leaderboard_top = 100
            if acc.tier == 'A':
                limits = tier_collection.A
            elif acc.tier == 'B':
                limits = tier_collection.B
            else:
                limits = tier_collection.C

            if costs < limits.total_costs_limit:
                if today_volume < limits.daily_bridge_volume_limit:
                    if today_txs < limits.daily_bridge_txs_limit:
                        if leaderboard_top > limits.leaderboard_top_limit:
                            logger.info(f'#{acc.id} | {acc.address} | '
                                        f'will be used for main_taiko with {balance.float} $ETH on taiko.')
                            accs.append((acc, balance.float))
                        else:
                            logger.warning(
                                f'#{acc.id} | {acc.address} | will not be used because of leaderboard limit. '
                                f'current: {leaderboard_top}% with limit {limits.leaderboard_top_limit}%.')
                    else:
                        logger.warning(
                            f'#{acc.id} | {acc.address} | will not be used because of txs limit. '
                            f'current: {today_txs} txs with limit {limits.daily_bridge_txs_limit} txs.')
                else:
                    logger.warning(
                        f'#{acc.id} | {acc.address} | will not be used because of volume limit. '
                        f'current: {round(today_volume, 6)} $ETH with limit {limits.daily_bridge_volume_limit} $ETH.')
            else:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used because of costs limit. '
                    f'current: {round(costs, 6)} $ETH with limit {limits.total_costs_limit} $ETH.')

    if shuffle:
        random.shuffle(accs)

    accs.sort(key=lambda x: x[1], reverse=True)
    return [acc[0] for acc in accs]


def sql_get_accs_to_withdraw(sql: SQL,
                             day: str,
                             shuffle: bool = False,
                             filter_low_balance: bool = True,
                             minimum_required_balance: float = 0.0001) -> List[AccountItem]:
    total_accs = sql_get_accs(sql=sql)

    accs = []
    for acc in total_accs:
        balance = get_balance(address=acc.address, rpc=taiko_chain.rpc)

        if filter_low_balance and balance.float <= minimum_required_balance:
            logger.warning(
                f'#{acc.id} | {acc.address} | will not be used because of low balance: '
                f'{balance.float} $ETH on taiko, minimum required: {round(minimum_required_balance, 6)} $ETH.'
            )
            continue

        logger.info(f'#{acc.id} | {acc.address} | will be used for withdraw_taiko with {balance.float} $ETH on taiko.')
        accs.append((acc, balance.float))

    if shuffle:
        random.shuffle(accs)

    accs.sort(key=lambda x: x[1], reverse=True)
    return [acc[0] for acc in accs]


def sql_get_accs_to_deposit(sql: SQL, day: str,
                            shuffle: bool = False,
                            filter_low_balance: bool = True) -> List[AccountItem]:
    total_accs = sql_get_accs(sql=sql)
    total_trailblazers = get_total_trailblazer_count(address=total_accs[0].address)

    accs = []
    for acc in total_accs:
        if acc.tier:
            max_balance = 0
            max_balance_chain = None

            for chain in source_chains:
                try:
                    balance = get_balance(address=acc.address, rpc=chain.rpc)
                except:
                    balance = Balance(float=0, int=0)

                if balance.float > max_balance:
                    max_balance = balance.float
                    max_balance_chain = chain.name

            if filter_low_balance and max_balance <= minimum_transfer * 0.8:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used for deposit because of low balance: '
                    f'{max_balance} $ETH on {max_balance_chain}, minimum required: {round(minimum_transfer * 0.8, 6)} $ETH.'
                )
                continue

            costs = sql.get_total_costs(acc_id=acc.id)
            today_txs = sql.get_today_txs(day=day, acc_id=acc.id)
            today_volume = sql.get_today_volume(day=day, acc_id=acc.id)
            rank = sql.get_rank(acc_id=acc.id)
            if rank:
                leaderboard_top = round(rank / total_trailblazers * 100, 2)
            else:
                leaderboard_top = 100
            if acc.tier == 'A':
                limits = tier_collection.A
            elif acc.tier == 'B':
                limits = tier_collection.B
            else:
                limits = tier_collection.C

            if costs < limits.total_costs_limit:
                if today_volume < limits.daily_bridge_volume_limit:
                    if today_txs < limits.daily_bridge_txs_limit:
                        if leaderboard_top > limits.leaderboard_top_limit:
                            logger.info(f'#{acc.id} | {acc.address} | '
                                        f'will be used for deposit with {max_balance} $ETH on {max_balance_chain}.')
                            accs.append((acc, max_balance, max_balance_chain))
                        else:
                            logger.warning(
                                f'#{acc.id} | {acc.address} | will not be used because of leaderboard limit. '
                                f'current: {leaderboard_top}% with limit {limits.leaderboard_top_limit}%.')
                    else:
                        logger.warning(
                            f'#{acc.id} | {acc.address} | will not be used because of txs limit. '
                            f'current: {today_txs} txs with limit {limits.daily_bridge_txs_limit} txs.')
                else:
                    logger.warning(
                        f'#{acc.id} | {acc.address} | will not be used because of volume limit. '
                        f'current: {round(today_volume, 6)} $ETH with limit {limits.daily_bridge_volume_limit} $ETH.')
            else:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used because of costs limit. '
                    f'current: {round(costs, 6)} $ETH with limit {limits.total_costs_limit} $ETH.')

    if shuffle:
        random.shuffle(accs)

    accs.sort(key=lambda x: x[1], reverse=True)
    return [acc[0] for acc in accs]


def sql_add_burners(accs: List[AccountItem], sql: SQL):
    for acc in accs:
        private_key = generate_private_key()
        last_edited = datetime.now().isoformat()
        sql.add_burner(BurnerItem(id=acc.id, private_key=private_key, last_edited=last_edited))
