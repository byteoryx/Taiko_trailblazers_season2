import random
from datetime import datetime

from loguru import logger

from data.constants import (
    taikodrips_minimum_amount, taikodrips_contract, taiko_token, eth_token
)
from datatypes.account import AccountItem, DayBridgeItem
from datatypes.crypto import Balance
from modules.ritsu import ritsu_token_swap
from sdk.sql import SQL
from tools.coingecko import get_asset_price
from tools.crypto import (
    get_allowance,
    get_taikodrips_lockups, taikodrips_approve_tx, taikodrips_stake_tx, get_balance, get_balance_of
)
from tools.other_utils import sleep_in_range
from user_data.chains import taiko_chain
from user_data.config import sleep_between_txs_in_sec


def taikodrips_stake(sql: SQL, day: str, account: AccountItem, stake_limits: [float, float]):
    old_eth_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)

    total_stake = get_taikodrips_total_staked(private_key=account.private_key)
    taiko_balance = get_balance_of(address=account.address, contract=taiko_token.address)

    if (isinstance(stake_limits, str) and stake_limits == 'MAX') \
            or (stake_limits[0] <= taiko_balance.float <= stake_limits[1]):
        amount_to_stake = Balance(
            float=taiko_balance.float,
            int=taiko_balance.int
        )
    elif taiko_balance.float > stake_limits[1]:
        amount_to_stake_float = round(
            random.uniform(stake_limits[0], stake_limits[1]) - total_stake,
            random.randint(2, 4)
        )
        amount_to_stake = Balance(
            float=amount_to_stake_float,
            int=int(amount_to_stake_float * taiko_token.denomination)
        )
    else:
        amount_to_stake_float = max(
            round(random.uniform(stake_limits[0], stake_limits[1]) - total_stake, random.randint(2, 4)),
            taikodrips_minimum_amount
        )
        amount_to_stake = Balance(
            float=amount_to_stake_float,
            int=int(amount_to_stake_float * taiko_token.denomination)
        )

    while taiko_balance.float < amount_to_stake.float:
        eth_price = get_asset_price(ticker=eth_token.coingecko_ticker, proxy=account.proxy)
        taiko_price = get_asset_price(ticker=taiko_token.coingecko_ticker, proxy=account.proxy)

        amount_to_buy = round(amount_to_stake.float - taiko_balance.float, 4)
        amount_to_spend_float = taiko_price * amount_to_buy / eth_price
        amount_to_spend = Balance(
            float=amount_to_spend_float,
            int=int(amount_to_spend_float * eth_token.denomination)
        )

        leave_on_source = account.config.common.leave_balance_on_taiko_chain
        if old_eth_balance.float > amount_to_spend.float + leave_on_source:
            ritsu_token_swap(
                index=account.id,
                private_key=account.private_key,
                source_token=eth_token,
                destination_token=taiko_token,
                day=day,
                sql=sql,
                source_amount_to_spend=amount_to_spend,
                proxy=account.proxy
            )

            taiko_balance = get_balance_of(address=account.address, contract=taiko_token.address)
            if stake_limits[0] <= taiko_balance.float <= stake_limits[1]:
                amount_to_stake = taiko_balance

        else:
            logger.warning(
                f"#{account.id} | {account.address} | "
                f"not enough $ETH to buy {amount_to_buy} $TAIKO. "
                f"actual balance: {old_eth_balance.float} $ETH, "
                f"min. required: {round(amount_to_spend.float + leave_on_source, 5)} $ETH."
            )
            return

    if amount_to_stake.int:
        logger.info(f"#{account.id} | {account.address}: {amount_to_stake.float} $TAIKO to be staked on taikodrips.")
        allowance = get_allowance(
            private_key=account.private_key,
            token=taiko_token,
            spender_address=taikodrips_contract
        )
        if allowance.int < amount_to_stake.int:
            approve_amount = amount_to_stake.int
            approve_hash = taikodrips_approve_tx(
                token=taiko_token,
                approve_amount=approve_amount,
                private_key=account.private_key
            )
            if approve_hash:
                logger.info(
                    f'#{account.id} | {account.address}: approve to spend '
                    f'{round(approve_amount / taiko_token.denomination, 2)} $TAIKO | '
                    f'{taiko_chain.explorer}/{approve_hash}'
                )
                sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
            else:
                logger.error(
                    f'#{account.id} | {account.address}: approve to spend '
                    f'{amount_to_stake.float} $TAIKO tx has failed.'
                )

        tx_hash = taikodrips_stake_tx(
            private_key=account.private_key,
            amount_to_stake=amount_to_stake.int,
            lock_duration=random.choice(account.config.modules.taikodrips_lock_in_days_range)
        )
        if tx_hash:
            total_stake = get_taikodrips_total_staked(private_key=account.private_key)
            new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
            new_costs = old_eth_balance.float - new_balance.float

            volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=account.id)
            status = sql.add_day_report(
                day_item=DayBridgeItem(
                    id=account.id,
                    txs=txs,
                    volume=volume,
                    costs=costs + new_costs,
                    last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ),
                day=day,
                acc_id=account.id
            )
            logger.info(
                f'#{account.id} | {account.address}: '
                f'{total_stake} $TAIKO staked on taikodrips | '
                f'{taiko_chain.explorer}/{tx_hash} | {status}.'
            )
            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{account.id} | {account.address}: taikodrips tx has failed.')
    else:
        logger.warning(f"#{account.id} | {account.address}: nothing to stake, balance is empty.")


def get_taikodrips_total_staked(private_key: str):
    lockups = get_taikodrips_lockups(private_key=private_key)
    total_stake = round(sum(item.amount for item in lockups) / taiko_token.denomination, 2)
    return total_stake


def get_sql_formated_lockup_items(private_key: str) -> str:
    lockups = get_taikodrips_lockups(private_key=private_key)
    result = []

    for item in lockups:
        lockup_end_timestamp = item.timestamp + item.lockup
        lockup_end_date = datetime.utcfromtimestamp(lockup_end_timestamp).strftime('%b %d, %Y')
        amount_taiko = round(item.amount / taiko_token.denomination, 2)
        result.append(f"{amount_taiko} - {lockup_end_date}")

    return "; ".join(result)


def taikodrips_main(
        account: AccountItem,
        sql: SQL,
        day: str
):
    stake_limits = account.config.modules.taikodrips_stake_amount_range
    total_stake = get_taikodrips_total_staked(private_key=account.private_key)

    if isinstance(stake_limits, str):
        taikodrips_stake(
            sql=sql,
            day=day,
            account=account,
            stake_limits=stake_limits
        )
    elif stake_limits[1] > 0:
        if total_stake < stake_limits[0]:
            taikodrips_stake(
                sql=sql,
                day=day,
                account=account,
                stake_limits=stake_limits
            )
        else:
            logger.info(f"#{account.id} | {account.address}: {total_stake} $TAIKO already staked on taikodrips.")
    else:
        logger.info(
            f"#{account.id} | {account.address}: "
            f"tier-{account.tier} limit for staking on taikodrips is [{stake_limits[0]}, {stake_limits[1]}]. "
            f"actual stake: {total_stake} $TAIKO."
        )

    lockup_string = get_sql_formated_lockup_items(private_key=account.private_key)
    status = sql.update_taikodrip_lockups(acc=account, lockup_string=lockup_string)
    if status:
        logger.info(f'#{account.id} | {account.address}: {status}.')
