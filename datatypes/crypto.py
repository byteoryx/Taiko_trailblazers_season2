from pydantic import BaseModel


class Balance(BaseModel):
    int: int
    float: float


class Token(BaseModel):
    address: str
    ticker: str
    coingecko_ticker: str
    denomination: int
