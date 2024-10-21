import random

from loguru import logger
from web3 import Web3

from data.constants import taiko_weth_contract
from tools.crypto import get_balance, wrap_tx, get_balance_of, unwrap_tx
from tools.other_utils import sleep_in_range
from user_data.chains import taiko_chain
from user_data.config import sleep_between_txs_in_sec


def wrap_main(
        index: int,
        private_key: str,
        multiplier_range: (float, float),
        unwrap_only: bool = False
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
    minimum_required_balance = 0.0001

    if not unwrap_only:
        if balance.float > minimum_required_balance:
            amount_to_wrap = round(
                (balance.float - minimum_required_balance) *
                random.uniform(multiplier_range[0], multiplier_range[1]),
                random.randint(5, 7)
            )
            logger.info(f'#{index} | {account.address}: {balance.float} $ETH on {taiko_chain.name}, '
                        f'{amount_to_wrap} $ETH to wrap.')

            wrap = wrap_tx(
                private_key=private_key,
                amount_to_wrap=amount_to_wrap
            )
            if wrap:
                logger.info(f'#{index} | {account.address}: wrap {amount_to_wrap} $ETH | {taiko_chain.explorer}/{wrap}')
                sleep_in_range(sec_from=10 + sleep_between_txs_in_sec[0], sec_to=10 + sleep_between_txs_in_sec[1])
            else:
                logger.error(f'#{index} | {account.address}: wrap {amount_to_wrap} $ETH tx has failed.')
        else:
            logger.warning(f'#{index} | {account.address}: wrap | {balance.float} on {taiko_chain.name}, '
                           f'minimum required: {minimum_required_balance} $ETH.')

    weth_balance = get_balance_of(contract=taiko_weth_contract, address=account.address)
    if weth_balance.int:
        tx = unwrap_tx(
            private_key=private_key,
            amount_to_unwrap=weth_balance
        )
        if tx:
            logger.info(
                f'#{index} | {account.address}: unwrap {weth_balance.float} $wETH | {taiko_chain.explorer}/{tx}')
        else:
            logger.error(f'#{index} | {account.address}: unwrap {weth_balance.float} $wETH tx has failed.')
    else:
        logger.info(f'#{index} | {account.address}: nothing to unwrap.')
