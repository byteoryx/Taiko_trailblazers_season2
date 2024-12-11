from typing import Optional

from pydantic import BaseModel

from user_data.tiers import TierItem


class AccountItem(BaseModel):
    id: Optional[int]
    private_key: str
    address: Optional[str]
    cex_address: Optional[str]
    proxy: Optional[str]
    owner: str
    tier: str
    config: Optional[TierItem]
    last_edited: str


class BurnerItem(BaseModel):
    id: Optional[int]
    private_key: str
    address: Optional[str]
    last_edited: str


class DayBridgeItem(BaseModel):
    id: Optional[int]
    txs: int
    volume: float
    costs: float
    last_edited: str


class TrailblazersItem(BaseModel):
    id: Optional[int]
    domain: str
    badge_ids: Optional[str]
    points: int
    rank: int
    last_edited: Optional[str]


class BadgeItem(BaseModel):
    id: Optional[int]
    minted: str
    last_edited: str
