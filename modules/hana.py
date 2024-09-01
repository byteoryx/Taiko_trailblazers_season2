import random

from loguru import logger
from web3 import Web3

from datatypes.crypto import usdc_token, taiko_token, eth_token, Balance, Token
from modules.ritsu import ritsu_single_swap
from sdk.sql import SQL
from settings.chains import taiko_chain
from settings.config import leave_on_source, sleep_between_txs_in_sec, minimum_transfer
from settings.constants import hana_weth_supplied_contract, hana_taiko_debt_contract, hana_usdc_debt_contract, \
    hana_weth_debt_contract, taiko_taiko_contract, taiko_usdc_contract
from tools.coingecko import get_asset_price
from tools.crypto import get_balance, hana_withdraw_tx, get_balance_of, hana_repay_tx, hana_approve_tx, hana_supply_tx, \
    hana_borrow_tx
from tools.other_utils import sleep_in_range


def hana_repay(index: int, address: str, private_key: str, day: str, sql: SQL):
    def repay_debt(debt_balance: Balance, token: Token, token_contract: str = '', token_denomination: int = 10 ** 18):
        if debt_balance.int:
            if token.ticker != 'ETH':
                token_balance = get_balance_of(contract=token_contract, address=address,
                                               denomination=token_denomination)
            else:
                token_balance = get_balance(address=address, rpc=taiko_chain.rpc)

            eth_balance = get_balance(address=address, rpc=taiko_chain.rpc)

            if token_balance.int <= debt_balance.int:
                if token.ticker != 'ETH':
                    required_balance_int = int(debt_balance.int * 1.001)
                    to_buy_amount_int = required_balance_int - token_balance.int
                    to_buy_amount_float = round(to_buy_amount_int / token_denomination, 18)
                    to_buy_amount_in_usd = to_buy_amount_float * get_asset_price(ticker=token.coingecko_ticker)
                    source_amount_to_spend_float = to_buy_amount_in_usd / get_asset_price(
                        ticker=eth_token.coingecko_ticker)
                    source_amount_to_spend = Balance(
                        float=source_amount_to_spend_float,
                        int=int(source_amount_to_spend_float * eth_token.denomination)
                    )

                    if eth_balance.float > source_amount_to_spend.float:
                        ritsu_single_swap(
                            index=index,
                            private_key=private_key,
                            source_token=eth_token,
                            destination_token=token,
                            day=day,
                            sql=sql,
                            source_amount_to_spend=source_amount_to_spend
                        )
                    else:
                        logger.warning(f'#{index} | {address}: ritsu_swap | '
                                       f'not enough balance: want to spend: {source_amount_to_spend.float} $ETH, '
                                       f'but have only {eth_balance.float} $ETH.')

            approve_and_repay(token, debt_balance.int)

    def approve_and_repay(token: Token, debt_amount_int: int):
        if token.ticker != 'ETH':
            approve_hash = hana_approve_tx(
                token=token,
                approve_amount=int(debt_amount_int * 1.001),
                private_key=private_key
            )
            if approve_hash:
                logger.info(
                    f'#{index} | {address}: approve to spend '
                    f'{round(debt_amount_int * 1.001 / token.denomination, 6)} ${token.ticker} | '
                    f'{taiko_chain.explorer}/{approve_hash}'
                )
                sleep_in_range(sec_from=sleep_between_txs_in_sec[0], sec_to=sleep_between_txs_in_sec[1])
            else:
                logger.error(
                    f'#{index} | {address}: approve to spend '
                    f'{round(debt_amount_int * 1.001 / token.denomination, 6)} ${token.ticker} tx has failed.'
                )

        debt_balances = get_debt_balances(address)
        debt_amount = debt_balances[token.ticker if token.ticker != 'ETH' else 'WETH']

        if token.ticker != 'ETH':
            debt_token_actual_balance = get_balance_of(contract=token.address, address=address,
                                                       denomination=token.denomination)
        else:
            debt_token_actual_balance = get_balance(address=address, rpc=taiko_chain.rpc)

        if debt_token_actual_balance.int < debt_amount.int:
            if token.ticker != 'ETH':
                debt_amount.float = round(debt_token_actual_balance.int / token.denomination, 6)
                debt_amount.int = debt_token_actual_balance.int
            else:
                debt_amount.float = round(debt_token_actual_balance.float - leave_on_source, 6)
                debt_amount.int = int((debt_token_actual_balance.float - leave_on_source) * 10 ** 18)

        if debt_amount.int > 0:
            tx_hash = hana_repay_tx(
                private_key=private_key,
                repay_amount=debt_amount.int,
                repay_token=token
            )
            if tx_hash:
                logger.info(f'#{index} | {address}: hana_repay {debt_amount.float} ${token.ticker} | '
                            f'{taiko_chain.explorer}/{tx_hash}')
                sleep_in_range(sec_from=120 + sleep_between_txs_in_sec[0], sec_to=120 + sleep_between_txs_in_sec[1])
            else:
                logger.error(f'#{index} | {address}: hana_repay {debt_amount.float} ${token.ticker} '
                             f'tx has failed.')
        else:
            logger.warning(f'#{index} | {address}: hana_repay | not enough balance.')

    debt_balances = get_debt_balances(address)
    message = format_debt_message(debt_balances)
    logger.info(f'#{index} | {address}: hana_debts | {message if message else "no"}.')

    tickers = ['TKO', 'WETH', 'USDC']
    random.shuffle(tickers)
    for ticker in tickers:
        if ticker == 'TKO':
            repay_debt(debt_balances['TKO'], taiko_token, taiko_taiko_contract)
        elif ticker == 'WETH':
            repay_debt(debt_balances['WETH'], eth_token)
        elif ticker == 'USDC':
            repay_debt(debt_balances['USDC'], usdc_token, taiko_usdc_contract, token_denomination=10 ** 6)


def get_debt_balances(address: str):
    return {
        'WETH': get_balance_of(contract=hana_weth_debt_contract, address=address),
        'TKO': get_balance_of(contract=hana_taiko_debt_contract, address=address),
        'USDC': get_balance_of(contract=hana_usdc_debt_contract, address=address, denomination=10 ** 6)
    }


def format_debt_message(balances):
    return ', '.join(f"{balance.float} ${ticker}" for ticker, balance in balances.items() if balance.int)


def hana_borrow(index: int, address: str, private_key: str):
    old_debt_balances = get_debt_balances(address=address)
    message = format_debt_message(old_debt_balances)

    supplied_eth_amount = get_balance_of(contract=hana_weth_supplied_contract, address=address)

    logger.info(f'#{index} | {address}: hana_debts | {message if message else "no"}, '
                f'supplied: {supplied_eth_amount.float} $ETH.')

    supplied_eth_amount_in_usd = round(get_asset_price(ticker='ethereum') * supplied_eth_amount.float, 2)
    maximum_borrow_in_usd = supplied_eth_amount_in_usd * random.uniform(0.5, 0.7)

    token_to_borrow = random.choice([usdc_token, taiko_token, eth_token])
    token_to_borrow_price = get_asset_price(ticker=token_to_borrow.coingecko_ticker)
    amount_to_borrow = round(maximum_borrow_in_usd / token_to_borrow_price, random.randint(5, 7))

    if amount_to_borrow:
        tx_hash = hana_borrow_tx(
            private_key=private_key,
            borrow_amount=int(amount_to_borrow * token_to_borrow.denomination),
            borrow_token=token_to_borrow
        )
        if tx_hash:
            logger.info(f'#{index} | {address}: hana_borrow {amount_to_borrow} ${token_to_borrow.ticker} | '
                        f'{taiko_chain.explorer}/{tx_hash}')
            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{index} | {address}: hana_borrow tx has failed.')

    new_debt_balances = get_debt_balances(address=address)
    message = format_debt_message(new_debt_balances)

    logger.info(f'#{index} | {address}: hana_debts | {message if message else "no"}, '
                f'supplied: {supplied_eth_amount.float} $ETH.')


def hana_main(
        index: int,
        private_key: str,
        sql: SQL,
        day: str,
        multiplier_range: (float, float),
        only_withdraw: bool = False
):
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)

    if only_withdraw:
        hana_repay(index=index, address=account.address, private_key=private_key, day=day, sql=sql)
        hana_repay(index=index, address=account.address, private_key=private_key, day=day, sql=sql)
    else:
        old_balance = get_balance(address=account.address, rpc=taiko_chain.rpc)
        supply_amount = round(
            (old_balance.float - leave_on_source) *
            random.uniform(multiplier_range[0], multiplier_range[1]),
            random.randint(5, 7)
        )

        if supply_amount > minimum_transfer:
            supply_tx_hash = hana_supply_tx(
                private_key=private_key,
                supply_amount=supply_amount
            )
            if supply_tx_hash:
                logger.info(f'#{index} | {account.address}: hana_supply {supply_amount} $ETH | '
                            f'{taiko_chain.explorer}/{supply_tx_hash}')
                sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
            else:
                logger.error(f'#{index} | {account.address}: hana_supply tx has failed.')

        if random.choice([True, False]):
            hana_borrow(index=index, address=account.address, private_key=private_key)
            hana_repay(index=index, address=account.address, private_key=private_key, day=day, sql=sql)

    weth_supplied_balance = get_balance_of(contract=hana_weth_supplied_contract, address=account.address)
    if weth_supplied_balance.float > 0.0001:
        withdraw_tx_hash = hana_withdraw_tx(
            private_key=private_key,
            withdraw_amount=weth_supplied_balance.int
        )

        if withdraw_tx_hash:
            logger.info(f'#{index} | {account.address}: hana_withdraw | {taiko_chain.explorer}/{withdraw_tx_hash}')
            sleep_in_range(sec_from=60 + sleep_between_txs_in_sec[0], sec_to=60 + sleep_between_txs_in_sec[1])
        else:
            logger.error(f'#{index} | {account.address}: hana_withdraw tx has failed.')
    else:
        logger.warning(f'#{index} | {account.address}: hana_withdraw | supplied: ${weth_supplied_balance.int}.')
