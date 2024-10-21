import random
from datetime import datetime
from typing import List

from loguru import logger
from web3 import Web3

from datatypes.account import AccountItem, BurnerItem, BadgeItem
from datatypes.crypto import Balance
from sdk.sql import SQL
from tools.crypto import get_balance, generate_private_key
from tools.other_utils import get_leave_on_source
from tools.trailblazers import get_total_trailblazer_count
from user_data.chains import source_chains, taiko_chain
from user_data.config import minimum_transfer
from user_data.tiers import tier_collection


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
                cex_address=acc[2],
                proxy=acc[3],
                owner=acc[4],
                tier=acc[5],
                last_edited=acc[6],
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
                    cex_address=acc.cex_address,
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
                cex_address=acc[2],
                proxy=acc[3],
                owner=acc[4],
                tier=acc[5],
                last_edited=acc[6]
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

            if minimum_required_balance and balance.float < minimum_required_balance:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used because of low balance: '
                    f'{balance.float} $ETH on taiko, minimum required: {round(minimum_required_balance, 6)} $ETH.'
                )
                continue

            costs = sql.get_total_costs(acc_id=acc.id)
            rank = sql.get_rank(acc_id=acc.id)
            txs = sql.get_today_txs(day=day, acc_id=acc.id)
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
                if txs < limits.daily_txs_limit:
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
                        f'#{acc.id} | {acc.address} | will not be used because of daily txs limit. '
                        f'current: {txs} txs with limit {limits.daily_txs_limit} txs.')
            else:
                logger.warning(
                    f'#{acc.id} | {acc.address} | will not be used because of costs limit. '
                    f'current: {round(costs, 6)} $ETH with limit {limits.total_costs_limit} $ETH.')

    if shuffle:
        random.shuffle(accs)

    accs.sort(key=lambda x: x[1], reverse=True)
    return [acc[0] for acc in accs]


def sql_get_accs_to_deposit(
        sql: SQL,
        day: str,
        shuffle: bool = False,
        filter_low_balance: bool = True
) -> List[AccountItem]:
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

            leave_on_source = get_leave_on_source(tier=acc.tier, chain=max_balance_chain)
            if filter_low_balance and max_balance <= minimum_transfer + leave_on_source:
                logger.warning(
                    f'#{acc.id} | {acc.address} | '
                    f'the richest chain is {max_balance_chain} with {max_balance} $ETH. '
                    f'minimum required: {round(minimum_transfer + leave_on_source, 6)} $ETH '
                    f'(transfer={minimum_transfer} + leave_on_{max_balance_chain}={leave_on_source}).'
                )
                continue

            costs = sql.get_total_costs(acc_id=acc.id)
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
