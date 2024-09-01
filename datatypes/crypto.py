from pydantic import BaseModel

from settings.constants import taiko_taiko_contract


class Balance(BaseModel):
    int: int
    float: float


class Token(BaseModel):
    address: str
    ticker: str
    coingecko_ticker: str
    denomination: int


eth_token = Token(
    address='0x0000000000000000000000000000000000000000',
    ticker='ETH',
    coingecko_ticker='ethereum',
    denomination=10 ** 18
)

weth_token = Token(
    address='0xA51894664A773981C6C112C43ce576f315d5b1B6',
    ticker='WETH',
    coingecko_ticker='ethereum',
    denomination=10 ** 18
)

usdc_token = Token(
    address='0x07d83526730c7438048d55a4fc0b850e2aab6f0b',
    ticker='USDC',
    coingecko_ticker='usd-coin',
    denomination=10 ** 6
)

taiko_token = Token(
    address=taiko_taiko_contract,
    ticker='TKO',
    coingecko_ticker='taiko',
    denomination=10 ** 18
)
