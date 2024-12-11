import json

from loguru import logger

from data.constants import eth_token
from datatypes.relay import RelayBridgeQuotes
from tools.session import get_proxied_session


def get_relay_bridge_quote(
        address: str,
        source_chain_id: int,
        recipient_chain_id: int,
        amount: float,
        proxy: str
):
    try:
        payload = {
            "user": address,
            "originChainId": source_chain_id,
            "destinationChainId": recipient_chain_id,
            "tradeType": "EXACT_INPUT",
            "amount": str(int(amount * eth_token.denomination)),
            "referrer": "relay.link/swap",
            "useExternalLiquidity": False,
            "originCurrency": eth_token.address,
            "destinationCurrency": eth_token.address,
            "recipient": address
        }

        response = get_proxied_session(proxy=proxy).post(
            url="https://api.relay.link/quote",
            json=payload
        )
        if 'Amount is higher than the available liquidity' in response.text:
            return 'Amount is higher than the available liquidity'
        else:
            return RelayBridgeQuotes.parse_obj(json.loads(response.content))
    except Exception as e:
        logger.exception(e)
