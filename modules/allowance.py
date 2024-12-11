import random
from datetime import datetime

from loguru import logger
from web3 import Web3

from data.constants import (
    usdc_token,
    usdce_token,
    usdt_token,
    usdte_token,
    taiko_token,
    wbtc_token,
    ritsu_swap_contract,
    swapsicle_swap_contract,
    izumi_swap_contract,
    soswap_swap_contract,
    henjun_swap_contract,
    bebop_swap_contract,
    dzap_swap_contract,
    kodo_swap_contract,
    random_approve_contract1,
    meridian_deposit_contract,
    kiloex_deposit_contract,
    hana_supply_contract,
    hana_token_repay_borrow_contract,
    random_approve_contract2,
    random_approve_contract4,
    random_approve_contract3,
    symm_liquidity_contract,
    dtx_liquidity_contract
)
from datatypes.account import DayBridgeItem
from datatypes.crypto import Balance
from sdk.sql import SQL
from tools.crypto import get_balance, get_allowance, decrease_allowance_tx, approve_tx, increase_allowance_tx
from tools.other_utils import sleep_in_range
from user_data.chains import taiko_chain
from user_data.config import sleep_between_txs_in_sec

TOKENS = [
    usdc_token, usdce_token, usdt_token, usdte_token, taiko_token, wbtc_token
]
CONTRACTS = [
    swapsicle_swap_contract, ritsu_swap_contract,
    izumi_swap_contract, soswap_swap_contract,
    kodo_swap_contract, henjun_swap_contract,
    dzap_swap_contract, bebop_swap_contract,

    meridian_deposit_contract, kiloex_deposit_contract,
    hana_supply_contract, hana_token_repay_borrow_contract,
    random_approve_contract1, random_approve_contract2,
    random_approve_contract3, random_approve_contract4,
    symm_liquidity_contract, dtx_liquidity_contract

]


def decrease_allowance_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > 0.00001:

        random.shuffle(TOKENS)
        random.shuffle(CONTRACTS)

        for token in TOKENS:
            for contract in CONTRACTS:
                allowance = get_allowance(private_key=private_key, spender_address=contract, token=token)
                if allowance.int:
                    tx = decrease_allowance_tx(
                        private_key=private_key,
                        revoke_amount=allowance.int,
                        token=token,
                        spender_address=contract
                    )
                    if tx:
                        new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                        new_costs = old_balance.float - new_balance.float

                        volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                        status = sql.add_day_report(
                            day_item=DayBridgeItem(
                                id=index,
                                txs=txs,
                                volume=volume,
                                costs=costs + new_costs,
                                last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ),
                            day=day,
                            acc_id=index
                        )
                        logger.info(
                            f'#{index} | {account.address}: decrease_allowance {allowance.float} ${token.ticker} | '
                            f'{taiko_chain.explorer}/{tx} | {status}.'
                        )
                        sleep_in_range(sleep_between_txs_in_sec[0], sleep_between_txs_in_sec[1])
                    else:
                        logger.error(f'#{index} | {account.address}: '
                                     f'decrease_allowance {allowance.float} ${token.ticker} tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: decrease_allowance | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: 0.00001 $ETH.')


def approve_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > 0.00001:

        random.shuffle(TOKENS)
        random.shuffle(CONTRACTS)

        tokens = random.sample(TOKENS, k=random.randint(0, 3))
        contracts = random.sample(CONTRACTS, k=random.randint(0, 3))

        for token in tokens:
            for contract in contracts:
                approve_amount_int = int(
                    round(
                        random.uniform(1, 1_000_000),
                        random.randint(2, 10)
                    ) * token.denomination
                )
                approve_amount = Balance(
                    int=approve_amount_int,
                    float=round(
                        approve_amount_int / token.denomination,
                        random.randint(2, 4)
                    )
                )
                tx = approve_tx(
                    private_key=private_key,
                    approve_amount=approve_amount.int,
                    token=token,
                    spender_address=contract
                )
                if tx:
                    new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                    new_costs = old_balance.float - new_balance.float

                    volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                    status = sql.add_day_report(
                        day_item=DayBridgeItem(
                            id=index,
                            txs=txs,
                            volume=volume,
                            costs=costs + new_costs,
                            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        day=day,
                        acc_id=index
                    )
                    logger.info(
                        f'#{index} | {account.address}: approve {approve_amount.float} ${token.ticker} | '
                        f'{taiko_chain.explorer}/{tx} | {status}.'
                    )
                    sleep_in_range(sleep_between_txs_in_sec[0], sleep_between_txs_in_sec[1])
                else:
                    logger.error(f'#{index} | {account.address}: '
                                 f'approve {approve_amount.float} ${token.ticker} tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: approve | {old_balance.float} $ETH on {taiko_chain.name}, '
                       f'minimum required: 0.00001 $ETH.')


def increase_allowance_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    if old_balance.float > 0.00001:

        random.shuffle(TOKENS)
        random.shuffle(CONTRACTS)

        tokens = random.sample(TOKENS, k=random.randint(0, 3))
        contracts = random.sample(CONTRACTS, k=random.randint(0, 3))

        for token in tokens:
            for contract in contracts:
                approve_amount_int = int(
                    round(
                        random.uniform(1, 1_000_000),
                        random.randint(2, 10)
                    ) * token.denomination
                )
                approve_amount = Balance(
                    int=approve_amount_int,
                    float=round(
                        approve_amount_int / token.denomination,
                        random.randint(2, 4)
                    )
                )
                tx = increase_allowance_tx(
                    private_key=private_key,
                    approve_amount=approve_amount.int,
                    token=token,
                    spender_address=contract
                )
                if tx:
                    new_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
                    new_costs = old_balance.float - new_balance.float

                    volume, txs, costs = sql.get_volume_and_txs_by_id(day=day, acc_id=index)
                    status = sql.add_day_report(
                        day_item=DayBridgeItem(
                            id=index,
                            txs=txs,
                            volume=volume,
                            costs=costs + new_costs,
                            last_edited=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ),
                        day=day,
                        acc_id=index
                    )
                    logger.info(
                        f'#{index} | {account.address}: increase_allowance {approve_amount.float} ${token.ticker} | '
                        f'{taiko_chain.explorer}/{tx} | {status}.'
                    )
                    sleep_in_range(sleep_between_txs_in_sec[0], sleep_between_txs_in_sec[1])
                else:
                    logger.error(f'#{index} | {account.address}: '
                                 f'increase_allowance {approve_amount.float} ${token.ticker} tx has failed.')
    else:
        logger.warning(
            f'#{index} | {account.address}: increase_allowance | {old_balance.float} $ETH on {taiko_chain.name}, '
            f'minimum required: 0.00001 $ETH.')


def random_allowance_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str
):
    decrease_allowance_main(index=index, private_key=private_key, sql=sql, day=day)
    tasks = [
        lambda: increase_allowance_main(index=index, private_key=private_key, sql=sql, day=day),
        lambda: approve_main(index=index, private_key=private_key, sql=sql, day=day)
    ]
    random.choice(tasks)()
    decrease_allowance_main(index=index, private_key=private_key, sql=sql, day=day)
