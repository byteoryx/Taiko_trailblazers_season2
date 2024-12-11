import random
import secrets
import time
from typing import List

from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_bytes
from loguru import logger
from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.middleware import geth_poa_middleware

from data.abi import ritsu_abi, taikodrips_abi, brigade_spin_abi, brigade_checkin_abi, oxastra_abi, hyperlane_abi
from data.constants import (
    orbiter_contract,
    taiko_weth_contract,
    conft_contract,
    conft_mint_price,
    omnihub_contract,
    rubyscore_contract,
    rhino_gm_price,
    hana_supply_contract,
    ritsu_swap_contract,
    xy_contracts,
    eth_contract,
    xy_aggregator_contract,
    ritsu_pools,
    hana_token_repay_borrow_contract,
    taiko_usdc_contract,
    taiko_taiko_contract,
    hana_eth_repay_borrow_contract,
    brigade_harvest_contract,
    crack_x_stack_contract,
    zypher2048_contract,
    week_badge_contract,
    meridian_deposit_contract,
    kiloex_deposit_contract,
    taiko_usdc_stg_contract,
    taikodrips_contract,
    brigade_spin_contract,
    brigade_capsule_contract,
    brigade_starship_contract,
    brigade_checkin_contract,
    brigade_claim_item_contract,
    oxastra_contract,
    rhino_deploy_contract_fee,
    rhino_deploy_contract_data,
    blazplay_mint_contract,
    openalchi_standart_mint_contract,
    openalchi_standart_mint_fee,
    meridian_eth_recipient_contract,
    owlto_deploy_contract_data,
    hyperlane_contracts,
    gas_zip_inbound_contract,
    season1_bonus_contract
)
from datatypes.account import AccountItem
from datatypes.crypto import Balance, Token
from datatypes.taikodrips import LockupItem
from tools.coingecko import get_asset_price
from tools.relay import get_relay_bridge_quote
from user_data.chains import ChainItem, taiko_chain
from user_data.config import gas_multiplier


def pad_to_32_bytes(value):
    return value.rjust(64, '0')


def generate_private_key() -> str:
    return secrets.token_hex(32)


def encode_data(method_hash, params):
    encoded_params = ''
    for param in params:
        if isinstance(param, int):
            encoded_params += pad_to_32_bytes(hex(param)[2:])
        elif isinstance(param, str) and param.startswith('0x'):
            encoded_params += pad_to_32_bytes(param[2:])
        else:
            raise ValueError("Unsupported parameter type")
    return method_hash + encoded_params


def get_balance(address: str, rpc: str):
    web3 = Web3(Web3.HTTPProvider(rpc))
    balance = web3.eth.get_balance(web3.to_checksum_address(address))
    return Balance(
        int=balance,
        float=round(web3.from_wei(balance, 'ether'), 6)
    )


def get_balance_of(contract: str, address: str, denomination: int = 10 ** 18):
    web3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    abi = '''
    [
        {
            "constant":true,
            "inputs":[{"name":"_owner","type":"address"}],
            "name":"balanceOf",
            "outputs":[{"name":"balance","type":"uint256"}],
            "type":"function"
        }
    ]
    '''

    token_contract = web3.eth.contract(address=web3.to_checksum_address(contract), abi=abi)
    balance = token_contract.functions.balanceOf(web3.to_checksum_address(address)).call()

    return Balance(
        int=balance,
        float=round(balance / denomination, 8)
    )


def wait_for_new_balance(old_balance: Balance, account: AccountItem, chain: ChainItem, token: Token = None) -> Balance:
    tries = 0
    while True:
        if not token:
            new_recipient_balance = get_balance(address=account.address, rpc=chain.rpc)
        else:
            new_recipient_balance = get_balance_of(
                address=account.address,
                contract=token.address,
                denomination=token.denomination
            )

        if new_recipient_balance.int != old_balance.int:
            return new_recipient_balance
        else:
            tries += 1
            if tries > 600:
                return new_recipient_balance
            time.sleep(1)


def sign_and_wait(w3: Web3, transaction: {}, private_key: str, timeout: int = 300):
    account = w3.eth.account.from_key(private_key)
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    try:
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=timeout)

        if receipt.status == 1:
            return txn_hash.hex()
        else:
            return None
    except TimeExhausted:
        logger.error(f"{account.address}: {txn_hash.hex()} not confirmed in {timeout} seconds.")
        return None
    except ValueError as e:
        logger.error(f"{account.address}: {e.args[0]}.")


def get_gas(w3: Web3()):
    latest_block = w3.eth.block_number
    fee_history = w3.eth.fee_history(1, latest_block, reward_percentiles=[50])
    base_fee_per_gas1 = fee_history['baseFeePerGas'][0]
    max_priority_fee_per_gas = int(fee_history['reward'][0][0])

    max_fee_per_gas = int(base_fee_per_gas1 + max_priority_fee_per_gas * 1.1)

    base_fee_per_gas2 = w3.eth.get_block('latest')['baseFeePerGas']
    if int(base_fee_per_gas2) > max_fee_per_gas:
        max_fee_per_gas = int(base_fee_per_gas2)

    return int(max_priority_fee_per_gas * 2), int(max_fee_per_gas * 3)


def get_account_nonce(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    return nonce


def orbiter_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    orbiter_recipient = w3.to_checksum_address(orbiter_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': orbiter_recipient,
        'value': Web3.to_wei(amount_to_bridge, 'ether') + recipient_chain.orbiter_code,
        'data': '0x'
    }) * gas_multiplier)

    transaction = {
        "chainId": source_chain.id,
        "from": account.address,
        "to": orbiter_recipient,
        "value": Web3.to_wei(amount_to_bridge, 'ether') + recipient_chain.orbiter_code,
        "data": "0x",
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def xy_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    recipient = w3.to_checksum_address(xy_contracts[source_chain.name])

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    method = '0xcdc65927'
    data = method + \
           pad_to_32_bytes('0').lower() + \
           pad_to_32_bytes(eth_contract[2:]).lower() + \
           pad_to_32_bytes(eth_contract[2:]).lower() + \
           pad_to_32_bytes(account.address[2:]).lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes('1a0').lower() + \
           pad_to_32_bytes(hex(recipient_chain.id)[2:]).lower() + \
           pad_to_32_bytes(eth_contract[2:]).lower() + \
           pad_to_32_bytes('0').lower() + \
           pad_to_32_bytes(hex(int(amount_to_bridge * 0.9 * 10 ** 18))[2:]).lower() + \
           pad_to_32_bytes('64').lower() + \
           pad_to_32_bytes(xy_aggregator_contract[2:]).lower() + \
           pad_to_32_bytes('1').lower() + \
           pad_to_32_bytes('0').lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': int(Web3.to_wei(amount_to_bridge, 'ether')),
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": source_chain.id,
        "from": account.address,
        "to": recipient,
        "value": int(Web3.to_wei(amount_to_bridge, 'ether')),
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def relay_bridge_tx(
        index: int,
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float,
        proxy: str
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    try:
        quote = get_relay_bridge_quote(
            address=account.address,
            source_chain_id=source_chain.id,
            recipient_chain_id=recipient_chain.id,
            amount=amount_to_bridge,
            proxy=proxy
        )
        if 'Amount is higher than the available liquidity' in quote:
            logger.error(f'#{index} | {account.address}: '
                         f'{amount_to_bridge} $ETH on {source_chain.name} is higher than the available liquidity.')
            return False

        data = quote.steps[0].items[0].data.data
        recipient = w3.to_checksum_address(quote.steps[0].items[0].data.to)
        value = quote.steps[0].items[0].data.value

        gas_limit = int(w3.eth.estimate_gas({
            "from": account.address,
            "to": recipient,
            "value": int(value),
            "data": data
        }) * gas_multiplier)

        transaction = {
            "chainId": source_chain.id,
            "from": account.address,
            "to": recipient,
            "value": int(value),
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def hyperlane_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    hyperlane_contract = w3.eth.contract(
        address=w3.to_checksum_address(hyperlane_contracts[source_chain.name.lower()]),
        abi=hyperlane_abi
    )

    amount_wei = int(amount_to_bridge * 10 ** 18)
    bridge_fee = hyperlane_contract.functions.quoteBridge(
        recipient_chain.id, amount_wei
    ).call()

    transaction = hyperlane_contract.functions.bridgeETH(
        recipient_chain.id, amount_wei
    ).build_transaction({
        'value': amount_wei + bridge_fee,
        'from': account.address,
        'chainId': source_chain.id,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    })

    gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
    transaction['gas'] = gas_limit

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def gas_zip_bridge_tx(
        private_key: str,
        source_chain: ChainItem,
        recipient_chain: ChainItem,
        amount_to_bridge: float
):
    w3 = Web3(Web3.HTTPProvider(source_chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = f"0x01" + hex(recipient_chain.gas_zip_code)[2:].zfill(4)

    gas_limit = int(w3.eth.estimate_gas({
        "from": account.address,
        "to": w3.to_checksum_address(gas_zip_inbound_contract),
        "value": int(amount_to_bridge * 10 ** 18),
        "data": data
    }) * gas_multiplier)

    transaction = {
        "chainId": source_chain.id,
        "from": account.address,
        "to": w3.to_checksum_address(gas_zip_inbound_contract),
        "value": int(amount_to_bridge * 10 ** 18),
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def wrap_tx(private_key: str, amount_to_wrap: float):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    weth_contract = w3.to_checksum_address(taiko_weth_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': weth_contract,
        'value': Web3.to_wei(amount_to_wrap, 'ether'),
        'data': '0xd0e30db0'
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": weth_contract,
        "value": Web3.to_wei(amount_to_wrap, 'ether'),
        "data": "0xd0e30db0",
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def unwrap_tx(private_key: str, amount_to_unwrap: Balance):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    weth_contract = w3.to_checksum_address(taiko_weth_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    method_hash = '0x2e1a7d4d'
    amount_hex = hex(amount_to_unwrap.int)[2:].zfill(64)
    data = method_hash + amount_hex

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': weth_contract,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": weth_contract,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def conft_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    conft_recipient = w3.to_checksum_address(conft_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': conft_recipient,
        'value': int(conft_mint_price * 10 ** 18),
        'data': '0x1249c58b'
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": conft_recipient,
        "value": int(conft_mint_price * 10 ** 18),
        "data": '0x1249c58b',
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def omnihub_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    omnihub_recipient = w3.to_checksum_address(omnihub_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': omnihub_recipient,
        'value': "0x5f7f37b39000",
        'data': '0xa0712d680000000000000000000000000000000000000000000000000000000000000001'
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": omnihub_recipient,
        "value": "0x5f7f37b39000",
        "data": '0xa0712d680000000000000000000000000000000000000000000000000000000000000001',
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def omnihub_tx2(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    omnihub_recipient = w3.to_checksum_address("0x7aAE1F74E36243A621AC04a4E9ACC64cbe56738F")

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0xa0712d680000000000000000000000000000000000000000000000000000000000000001"
    value = 10000000000001
    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': omnihub_recipient,
        'value': value,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": omnihub_recipient,
        "value": value,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def rubyscore_vote_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(rubyscore_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': '0x632a9a52'
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": '0x632a9a52',
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def transfer_tx(private_key: str, amount_to_send: float, chain: ChainItem = taiko_chain, address: str = ''):
    w3 = Web3(Web3.HTTPProvider(chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(private_key)

    if address:
        recipient = w3.to_checksum_address(address)
    else:
        recipient = account.address

    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': int(amount_to_send * 10 ** 18)
    }) * gas_multiplier)

    transaction = {
        "chainId": chain.id,
        "from": account.address,
        "to": recipient,
        "value": int(amount_to_send * 10 ** 18),
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def transfer_full_balance(private_key: str, recipient_addr: str, chain: ChainItem = taiko_chain):
    w3 = Web3(Web3.HTTPProvider(chain.rpc))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(private_key)
    recipient = w3.to_checksum_address(recipient_addr)

    nonce = w3.eth.get_transaction_count(account.address)
    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    balance = w3.eth.get_balance(account.address)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0
    }) * gas_multiplier)

    gas_cost = gas_limit * int(max_fee_per_gas * gas_multiplier)

    if balance <= gas_cost:
        return "not enough balance"
    else:
        amount_to_send = balance - gas_cost

        transaction = {
            "chainId": chain.id,
            "from": account.address,
            "to": recipient,
            "value": amount_to_send,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def rhino_tx(private_key: str, contract: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': int(rhino_gm_price * 10 ** 18),
        'data': '0xc0129d43'
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": int(rhino_gm_price * 10 ** 18),
        "data": '0xc0129d43',
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def rhino_deploy_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'value': rhino_deploy_contract_fee,
        'data': rhino_deploy_contract_data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        'value': rhino_deploy_contract_fee,
        'data': rhino_deploy_contract_data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def pad_hex(value, length=64):
    return value[2:].zfill(length)


def hana_supply_tx(private_key: str, supply_amount: float):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(hana_supply_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    from_address = '0xa51894664a773981c6c112c43ce576f315d5b1b6'
    to_address = account.address
    amount = 0

    from_address_padded = pad_hex(Web3.to_checksum_address(from_address)).lower()
    to_address_padded = pad_hex(Web3.to_checksum_address(to_address)).lower()
    amount_padded = pad_hex(hex(amount))

    data = '0x474cf53d' + from_address_padded + to_address_padded + amount_padded

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': int(supply_amount * 10 ** 18),
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": int(supply_amount * 10 ** 18),
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def hana_withdraw_tx(private_key: str, withdraw_amount: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(hana_supply_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    from_address = '0xa51894664a773981c6c112c43ce576f315d5b1b6'
    value_hex = hex(withdraw_amount)[2:].zfill(64)

    from_address_padded = pad_hex(Web3.to_checksum_address(from_address)).lower()
    value_padded = pad_hex(value_hex).lower()
    to_address_padded = pad_hex(Web3.to_checksum_address(account.address)).lower()

    data = '0x80500d20' + from_address_padded + value_padded + to_address_padded
    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "value": 0,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if '35' in e.args[0]:
            logger.error(
                f'{account.address}: '
                f'{e.args[0]} while withdrawing {round(withdraw_amount / 10 ** 18, 6)} $ETH, trying less amount.'
            )
            return hana_withdraw_tx(private_key=private_key, withdraw_amount=int(withdraw_amount * 0.999))
        else:
            logger.exception(e)


def hana_approve_tx(token: Token, approve_amount: int, private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x095ea7b3' + \
           pad_to_32_bytes(hana_token_repay_borrow_contract[2:]) + \
           pad_to_32_bytes(hex(approve_amount)[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def ritsu_approve_tx(token: Token, approve_amount: int, private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x095ea7b3' + \
           pad_to_32_bytes(ritsu_swap_contract[2:]) + \
           pad_to_32_bytes(hex(approve_amount)[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def meridian_approve_tx(token: Token, approve_amount: int, private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x095ea7b3' + \
           pad_to_32_bytes(meridian_deposit_contract[2:]) + \
           pad_to_32_bytes(hex(approve_amount)[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def kiloex_approve_tx(token: Token, approve_amount: int, private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x095ea7b3' + \
           pad_to_32_bytes(kiloex_deposit_contract[2:]) + \
           pad_to_32_bytes(hex(approve_amount)[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def hana_repay_tx(private_key: str, repay_amount: int, repay_token: Token):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(
        hana_token_repay_borrow_contract if repay_token.ticker != 'ETH' else hana_eth_repay_borrow_contract
    )

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x02c5fcf8' if repay_token.ticker == 'ETH' else '0x573ade81'

    if repay_token.ticker == 'USDC':
        data += pad_to_32_bytes(taiko_usdc_contract[2:])
    elif repay_token.ticker == 'ETH':
        data += pad_to_32_bytes(taiko_weth_contract[2:])
    elif repay_token.ticker == 'TKO':
        data += pad_to_32_bytes(taiko_taiko_contract[2:])

    data += pad_to_32_bytes(hex(repay_amount)[2:]) + pad_to_32_bytes('2') + pad_to_32_bytes(account.address[2:])
    data = data.lower()

    value = repay_amount if repay_token.ticker == 'ETH' else 0
    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': value,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": value,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def hana_borrow_tx(private_key: str, borrow_amount: int, borrow_token: Token):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(
        hana_token_repay_borrow_contract if borrow_token.ticker != 'ETH' else hana_eth_repay_borrow_contract
    )

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x66514c97' if borrow_token.ticker == 'ETH' else '0xa415bcad'

    if borrow_token.ticker == 'USDC':
        data += pad_to_32_bytes(taiko_usdc_contract[2:])
    elif borrow_token.ticker == 'ETH':
        data += pad_to_32_bytes(taiko_weth_contract[2:])
    elif borrow_token.ticker == 'TKO':
        data += pad_to_32_bytes(taiko_taiko_contract[2:])

    data += pad_to_32_bytes(hex(borrow_amount)[2:]) + pad_to_32_bytes('2') + pad_to_32_bytes('0')
    if borrow_token.ticker != 'ETH':
        data += pad_to_32_bytes(account.address[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def convert_address(address):
    return to_bytes(hexstr=pad_to_32_bytes(address[2:]))


def convert_uint(value):
    return to_bytes(hexstr=pad_to_32_bytes(hex(value)[2:]))


def get_amount_out_min(token_in_price: float,
                       amount_in: float,
                       token_out_price: float):
    amount_out = token_in_price * amount_in / token_out_price
    return amount_out


def get_steps(pair: str, address: str):
    if pair == 'ETH-USDC':
        return [generate_swap_step(
            pool=ritsu_pools["USDC"],
            token_from=taiko_weth_contract,
            address=address
        )]
    elif pair == 'ETH-TKO':
        return [
            generate_swap_step(
                pool=ritsu_pools["TKO"],
                token_from=taiko_weth_contract,
                address=address
            ),
        ]
    elif pair == 'USDCe-ETH':
        return [generate_swap_step(
            pool=ritsu_pools["USDCe"],
            token_from=taiko_usdc_stg_contract,
            address=address
        )]
    elif pair == 'ETH-USDCe':
        return [generate_swap_step(
            pool=ritsu_pools["USDCe"],
            token_from=taiko_weth_contract,
            address=address
        )]


def generate_swap_step(
        pool: str,
        token_from: str,
        address: str
):
    data = '0x' + pad_to_32_bytes(token_from[2:]).lower() + \
           pad_to_32_bytes(address[2:]).lower() + \
           pad_to_32_bytes('2').lower()

    step = {
        'pool': pool,
        'data': data,
        'callback': "0x0000000000000000000000000000000000000000",
        'callbackData': "0x"

    }
    return step


def ritsu_swap_tx(
        private_key: str,
        token_in: Token,
        token_out: Token,
        amount_in: int,
        proxy: str
):
    amount_out_min_float = get_amount_out_min(
        token_in_price=get_asset_price(ticker=token_in.coingecko_ticker, proxy=proxy),
        amount_in=round(amount_in / token_in.denomination, 10),
        token_out_price=get_asset_price(ticker=token_out.coingecko_ticker, proxy=proxy)
    )
    amount_out_min = int(amount_out_min_float * token_out.denomination * 0.8)
    if not amount_out_min:
        amount_out_min = 1

    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    ritsu_contract = w3.eth.contract(
        address=w3.to_checksum_address(ritsu_swap_contract),
        abi=ritsu_abi
    )

    transaction = ritsu_contract.functions.swap(
        [
            {
                'steps': get_steps(
                    pair=f"{token_in.ticker}-{token_out.ticker}",
                    address=account.address
                ),
                'tokenIn': token_in.address,
                'amountIn': amount_in
            }
        ],
        amount_out_min,
        int(time.time() + 120)
    ).build_transaction({
        'value': amount_in,
        'from': account.address,
        'chainId': taiko_chain.id,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    })

    gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
    transaction['gas'] = gas_limit

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def brigade_harvest_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(brigade_harvest_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': '0x4641257d'
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": '0x4641257d',
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "You can't harvest yet" in e.args[0]:
            return "you can't harvest yet"
        else:
            logger.exception(e)


def brigade_spin_tx(
        private_key: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    brigade_contract = w3.eth.contract(
        address=w3.to_checksum_address(brigade_spin_contract),
        abi=brigade_spin_abi
    )

    try:
        transaction = brigade_contract.functions.spinWheel().build_transaction({
            'from': account.address,
            'chainId': taiko_chain.id,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        })

        gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
        transaction['gas'] = gas_limit

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "You can't spin yet" in str(e):
            return "you can't spin yet"
        else:
            logger.exception(f"{account.address} | {e}")


def brigade_capsule_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(brigade_capsule_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0x3c9397d8" + pad_to_32_bytes(hex(random.randint(1, 10))[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "You can't pick a capsule yet" in e.args[0]:
            return "you can't pick a capsule yet"
        else:
            logger.exception(f"{account.address} | {e}")


def brigade_starship_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(brigade_starship_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0xa8cf7c69" + pad_to_32_bytes(hex(random.randint(1, 10))[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "You can't start yet" in e.args[0]:
            return "you can't start yet"
        else:
            logger.exception(f"{account.address} | {e}")


def brigade_checkin_tx(
        private_key: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    brigade_contract = w3.eth.contract(
        address=w3.to_checksum_address(brigade_checkin_contract),
        abi=brigade_checkin_abi
    )

    try:
        transaction = brigade_contract.functions.checkin().build_transaction({
            'from': account.address,
            'chainId': taiko_chain.id,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        })

        gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
        transaction['gas'] = gas_limit

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "You can't claim yet" in str(e):
            return "you can't claim yet"
        else:
            logger.exception(f"{account.address} | {e}")


def brigade_claim_item_tx(
        private_key: str,
        item_index: int
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(brigade_claim_item_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0xbb1ab0f5" + pad_to_32_bytes(hex(item_index)[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "Max claims reached for this product" in e.args[0]:
            return "max claims reached for this product"
        else:
            logger.exception(f"{account.address} | {e}")


def oxastra_boost_tx(
        private_key: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    brigade_contract = w3.eth.contract(
        address=w3.to_checksum_address(oxastra_contract),
        abi=oxastra_abi
    )

    try:
        transaction = brigade_contract.functions.boost().build_transaction({
            'from': account.address,
            'chainId': taiko_chain.id,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        })

        gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
        transaction['gas'] = gas_limit

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "AstraGameBoost available only once every 24 hours" in str(e):
            return "AstraGameBoost available only once every 24 hours"
        else:
            logger.exception(f"{account.address} | {e}")


def contract_deploy_tx(
        private_key: str,
        abi: [],
        bytecode: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    try:
        transaction = contract.constructor().build_transaction({
            'from': account.address,
            'chainId': taiko_chain.id,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        })

        gas_limit = int(w3.eth.estimate_gas(transaction=transaction) * gas_multiplier)
        transaction['gas'] = gas_limit

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(f"{account.address} | {e}")


def blazplay_mint_tx(
        private_key: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(blazplay_mint_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0x40d097c3" + pad_to_32_bytes(account.address[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(f"{account.address} | {e}")


def get_blazplay_balance(address: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    erc721_contract_address = w3.to_checksum_address(blazplay_mint_contract)
    erc721_minimal_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_tokenId", "type": "uint256"}],
            "name": "ownerOf",
            "outputs": [{"name": "owner", "type": "address"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=erc721_contract_address, abi=erc721_minimal_abi)
    balance = contract.functions.balanceOf(w3.to_checksum_address(address)).call()
    return balance


def openalchi_standart_mint_tx(
        private_key: str
):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(openalchi_standart_mint_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = "0x1167f452"

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data,
            'value': openalchi_standart_mint_fee
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "value": openalchi_standart_mint_fee,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "Already owns" in e.args[0]:
            return "already owns standard elements"
        else:
            logger.exception(f"{account.address} | {e}")


def crack_x_stack_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(crack_x_stack_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': '0x97e01a46'
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": '0x97e01a46',
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def generate_random_hash():
    random_bytes = secrets.token_bytes(32)
    random_hash = "0x" + random_bytes.hex()
    return random_hash


def zypher2048_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(zypher2048_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x36ab86c4' + pad_to_32_bytes(generate_random_hash()[2:]) + pad_to_32_bytes('1')

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': int(0.00025 * 10 ** 18),
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': int(0.00025 * 10 ** 18),
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def get_badge_signature(private_key: str, timestamp: int):
    account = Account.from_key(private_key)

    message = str(timestamp)

    encoded_data = encode_defunct(text=message)
    signed_message = account.sign_message(encoded_data)
    signature = signed_message.signature.hex()
    return signature


def week7_tx(private_key: str, message: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(week_badge_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x00257612' + \
           pad_to_32_bytes('40') + \
           pad_to_32_bytes('6') + \
           pad_to_32_bytes('41') + \
           message + \
           pad_to_32_bytes('0')

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if '0x9ea134e9' in e.message:
            return 'already minted'
        logger.exception(e)


def week8_tx(private_key: str, message: str, badge_id: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(week_badge_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x00257612' + \
           pad_to_32_bytes('40') + \
           pad_to_32_bytes(str(badge_id)) + \
           pad_to_32_bytes('41') + \
           message + \
           pad_to_32_bytes('0')

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if '0x9ea134e9' in e.message:
            return 'already minted'
        logger.exception(e)


def meridian_usdc_deposit_tx(private_key: str, deposit_int: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(meridian_deposit_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    data = '0xe8eda9df' + \
           pad_to_32_bytes(taiko_usdc_stg_contract[2:]) + \
           pad_to_32_bytes(hex(deposit_int)[2:]) + \
           pad_to_32_bytes(account.address[2:]) + \
           pad_to_32_bytes('0')

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': 0,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def meridian_eth_deposit_tx(private_key: str, deposit_int: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(meridian_eth_recipient_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    data = '0x474cf53d' + \
           pad_to_32_bytes(meridian_deposit_contract[2:]) + \
           pad_to_32_bytes(account.address[2:]) + \
           pad_to_32_bytes('0')

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': deposit_int,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': deposit_int,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def meridian_eth_withdraw_tx(private_key: str, withdraw_int: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(meridian_eth_recipient_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    data = '0x80500d20' + \
           pad_to_32_bytes(meridian_deposit_contract[2:]) + \
           pad_to_32_bytes(hex(withdraw_int)[2:]) + \
           pad_to_32_bytes(account.address[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': 0,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def meridian_usdc_withdraw_tx(private_key: str, withdraw_int: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(meridian_deposit_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    data = '0x69328dec' + \
           pad_to_32_bytes(taiko_usdc_stg_contract[2:]) + \
           pad_to_32_bytes(hex(withdraw_int)[2:]) + \
           pad_to_32_bytes(account.address[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': 0,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def taikodrips_approve_tx(token: Token, approve_amount: int, private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0x095ea7b3' + \
           pad_to_32_bytes(taikodrips_contract[2:]) + \
           pad_to_32_bytes(hex(approve_amount)[2:])

    data = data.lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def taikodrips_stake_tx(private_key: str, amount_to_stake: int, lock_duration: int):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(taikodrips_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)
    data = '0xe2bbb158' + \
           pad_to_32_bytes(hex(amount_to_stake)[2:]) + \
           pad_to_32_bytes(hex(lock_duration)[2:])

    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "data": data,
            'value': 0,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        logger.exception(e)


def get_allowance(private_key: str, spender_address: str, token: Token):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))

    account = w3.eth.account.from_key(private_key)
    owner_address = account.address

    min_abi = [
        {
            "constant": True,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "remaining", "type": "uint256"}],
            "type": "function"
        }
    ]

    token_contract = w3.eth.contract(address=w3.to_checksum_address(token.address), abi=min_abi)
    allowance = token_contract.functions.allowance(
        w3.to_checksum_address(owner_address), w3.to_checksum_address(spender_address)
    ).call()

    return Balance(
        int=allowance,
        float=round(allowance / token.denomination, 6)
    )


def get_taikodrips_lockups(private_key: str) -> [LockupItem]:
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))

    account = w3.eth.account.from_key(private_key)

    token_contract = w3.eth.contract(address=w3.to_checksum_address(taikodrips_contract), abi=taikodrips_abi)
    lockup_info = token_contract.functions.getUserLockUpArrays(account.address).call()

    lockup_items: List[LockupItem] = [
        LockupItem(timestamp=lockup_info[0][i], amount=lockup_info[1][i], lockup=lockup_info[2][i])
        for i in range(len(lockup_info[0]))
    ]

    return lockup_items


def decrease_allowance_tx(private_key: str, revoke_amount: int, token: Token, spender_address: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    revoke_amount_padded = revoke_amount.to_bytes(32, byteorder='big').hex()
    data = ('0xa457c2d7' +
            pad_to_32_bytes(spender_address[2:]) +
            pad_to_32_bytes(revoke_amount_padded[2:])).lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def approve_tx(private_key: str, approve_amount: int, token: Token, spender_address: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    approve_amount_padded = approve_amount.to_bytes(32, byteorder='big').hex()
    data = ('0x095ea7b3' +
            pad_to_32_bytes(spender_address[2:]) +
            pad_to_32_bytes(approve_amount_padded[2:])).lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def increase_allowance_tx(private_key: str, approve_amount: int, token: Token, spender_address: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(token.address)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    approve_amount_padded = approve_amount.to_bytes(32, byteorder='big').hex()
    data = ('0x39509351' +
            pad_to_32_bytes(spender_address[2:]) +
            pad_to_32_bytes(approve_amount_padded[2:])).lower()

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'to': recipient,
        'value': 0,
        'data': data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        "to": recipient,
        "value": 0,
        "data": data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def owlto_deploy_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    gas_limit = int(w3.eth.estimate_gas({
        'from': account.address,
        'value': 0,
        'data': owlto_deploy_contract_data
    }) * gas_multiplier)

    transaction = {
        "chainId": taiko_chain.id,
        "from": account.address,
        'value': 0,
        'data': owlto_deploy_contract_data,
        "gas": gas_limit,
        "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
        "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
        "nonce": nonce
    }

    return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)


def season1_bonus_claim_tx(private_key: str):
    w3 = Web3(Web3.HTTPProvider(taiko_chain.rpc))
    recipient = w3.to_checksum_address(season1_bonus_contract)

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    max_priority_fee_per_gas, max_fee_per_gas = get_gas(w3=w3)

    data = '0xf207564e' + hex(0)[2:].zfill(64)
    try:
        gas_limit = int(w3.eth.estimate_gas({
            'from': account.address,
            'to': recipient,
            'value': 0,
            'data': data
        }) * gas_multiplier)

        transaction = {
            "chainId": taiko_chain.id,
            "from": account.address,
            "to": recipient,
            "value": 0,
            "data": data,
            "gas": gas_limit,
            "maxFeePerGas": int(max_fee_per_gas * gas_multiplier),
            "maxPriorityFeePerGas": int(max_priority_fee_per_gas * gas_multiplier),
            "nonce": nonce
        }

        return sign_and_wait(w3=w3, transaction=transaction, private_key=private_key)
    except Exception as e:
        if "Already registered" in str(e):
            return "already registered"
        else:
            logger.exception(e)
