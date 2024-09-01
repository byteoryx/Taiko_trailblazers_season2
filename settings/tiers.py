from pydantic import BaseModel


class TierItem(BaseModel):
    leaderboard_top_limit: float  # in percent
    total_costs_limit: float  # in eth
    daily_bridge_txs_limit: int  # in txs
    daily_bridge_volume_limit: float  # in eth


class TierCollection(BaseModel):
    A: TierItem
    B: TierItem
    C: TierItem


tier_collection = TierCollection(
    A=TierItem(
        leaderboard_top_limit=1,
        total_costs_limit=0.0075,
        daily_bridge_txs_limit=5,
        daily_bridge_volume_limit=0.85
    ),
    B=TierItem(
        leaderboard_top_limit=5,
        total_costs_limit=0.005,
        daily_bridge_txs_limit=2,
        daily_bridge_volume_limit=0.85
    ),
    C=TierItem(
        leaderboard_top_limit=25,
        total_costs_limit=0.0025,
        daily_bridge_txs_limit=1,
        daily_bridge_volume_limit=0.85
    ),
)
