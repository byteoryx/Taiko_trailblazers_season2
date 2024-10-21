import json

import requests
from loguru import logger

from data.constants import badge_collection_contract
from datatypes.conft import CollectionItemsResponse, Nft, NonceResponse
from sdk.eth_account import Account
from sdk.eth_account.messages import encode_structured_data
from sdk.sql import SQL
from tools.session import get_proxied_session


def get_nft_items(address: str, session: requests.Session()):
    items = []

    page = 0
    while True:
        page += 1
        url = f"https://conft.app/wallet/taiko/{address}/nft/my-nfts?" \
              f"p={page}&_data=routes%2Fwallet.%24blockchain.%24address.nft.my-nfts"
        response = session.get(url=url)
        parsed_response = CollectionItemsResponse.parse_obj(json.loads(response.content))
        if parsed_response.walletNfts:
            if parsed_response.walletNfts.nfts:
                items.extend(parsed_response.walletNfts.nfts)
            else:
                break
        else:
            break

    return items


def get_badge_items(items: [Nft]):
    badge_items = []

    for item in items:
        if item.contractAddress.lower() == badge_collection_contract.lower():
            badge_items.append(item)

    return badge_items


def get_conft_nonce(session: requests.Session(), address: str):
    url = f"https://conft.app/connect?address={address}"
    response = session.get(url=url)
    return NonceResponse.parse_obj(json.loads(response.content))


def get_signature(private_key: str, nonce: str) -> str:
    account = Account.from_key(private_key)

    data = {
        "types": {
            "EIP712Domain": [],
            "Message": [
                {
                    "name": "text",
                    "type": "string"
                },
                {
                    "name": "nonce",
                    "type": "string"
                }
            ]
        },
        "primaryType": "Message",
        "domain": {},
        "message": {
            "text": "Welcome to coNFT! Please sign the message. This request does not trigger a transaction or cost any gas fees.",
            "nonce": nonce
        }
    }

    encoded_data = encode_structured_data(primitive=data)
    signed_message = account.sign_message(encoded_data)
    signature = signed_message.signature.hex()

    return signature


def post_signature(session: requests.Session(), address: str, signature: str):
    url = "https://conft.app/connect?_data=routes%2F_api.connect"
    payload = {
        "address": address,
        "signature": signature
    }
    response = session.post(url=url, data=payload)
    if 'address' in str(response.text):
        return True
    else:
        return False


def sign_data_root(session: requests.Session()):
    url = "https://conft.app/signin?_data=root"
    response = session.get(url=url)


def sign_data_routes(session: requests.Session()):
    url = "https://conft.app/signin?_data=routes%2Fsignin"
    response = session.get(url=url)


def nft_data_routes(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft?_data=routes%2Fwallet.%24blockchain.%24address"
    response = session.get(url=url)


def nft_data_routes_nft(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft?_data=routes%2Fwallet.%24blockchain.%24address.nft"
    response = session.get(url=url)


def nfts_root_nft(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft?_data=routes%2Fwallet.%24blockchain.%24address.nft"
    response = session.get(url=url)


def nft_my_nfts_root(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft/my-nfts?_data=root"
    response = session.get(url=url)


def nft_my_nfts_routes(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft/my-nfts?_data=routes%2Fwallet.%24blockchain.%24address"
    response = session.get(url=url)


def nft_my_nfts_routes_nft(session: requests.Session(), address: str):
    url = f"https://conft.app/wallet/taiko/{address}/nft/my-nfts?_data=routes%2Fwallet.%24blockchain.%24address.nft"
    response = session.get(url=url)


def register_address(proxy: str, address: str, private_key: str):
    session = get_proxied_session(proxy=proxy)
    nonce = get_conft_nonce(session=session, address=address)
    signature = get_signature(private_key=private_key, nonce=nonce.nonce.nonce)
    post_signature(session=session, address=address, signature=signature)
    sign_data_root(session=session)
    sign_data_routes(session=session)
    nft_data_routes(session=session, address=address)
    nft_data_routes_nft(session=session, address=address)
    nft_my_nfts_root(session=session, address=address)
    nft_my_nfts_routes(session=session, address=address)
    nft_my_nfts_routes_nft(session=session, address=address)


def get_owned_badges(
        id: int,
        sql: SQL,
        private_key: str,
        address: str,
        proxy: str
):
    old_owned_badges = sql.get_owned_badges(id=id)
    if old_owned_badges:
        register = False
    else:
        register = True
    tries = 0
    try:
        while True:
            try:
                tries += 1
                session = get_proxied_session(proxy=proxy)
                if register:
                    register_address(proxy=proxy, address=address, private_key=private_key)

                items = get_nft_items(address=address, session=session)
                badge_items = get_badge_items(items=items)

                other_badges = sorted(set([nft.name for nft in badge_items if nft.name and nft.name != 'Unknown']))
                unknown_badges = ['Unknown' for nft in badge_items if not nft.name]

                owned_badges = other_badges + unknown_badges

                nft_names_string = ", ".join(owned_badges)
                if nft_names_string:
                    return nft_names_string, len(owned_badges)
                if tries > 3:
                    return '', 0
            except Exception as e:
                logger.exception(e)
    except Exception as e:
        logger.exception(e)
        return '', 0
