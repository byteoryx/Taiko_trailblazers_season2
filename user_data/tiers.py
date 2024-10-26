from pydantic import BaseModel


class TierItem(BaseModel):
    leaderboard_top_limit: float  # in percent
    total_costs_limit: float  # in $ETH
    daily_txs_limit: int  # in transactions
    leave_balance_on_taiko_chain: float  # in $ETH
    leave_balance_on_source_chains: float  # in $ETH

    # если баланс $TAIKO меньше необходимого, скрипт постарается докупить недостающие токены на ritsu.xyz.
    # минимальный допустимый депозит - 0.01 $TAIKO.
    taikodrips_stake_amount_range: tuple[float, float]  # in $TAIKO


class TierCollection(BaseModel):
    A: TierItem
    B: TierItem
    C: TierItem


tier_collection = TierCollection(
    A=TierItem(
        leaderboard_top_limit=1,
        total_costs_limit=0.0075,
        daily_txs_limit=500,
        leave_balance_on_taiko_chain=0.011,
        leave_balance_on_source_chains=0.0011,
        taikodrips_stake_amount_range=(10, 11)
    ),
    B=TierItem(
        leaderboard_top_limit=5,
        total_costs_limit=0.005,
        daily_txs_limit=250,
        leave_balance_on_taiko_chain=0.0051,
        leave_balance_on_source_chains=0.0011,
        taikodrips_stake_amount_range=(1, 2)
    ),
    C=TierItem(
        leaderboard_top_limit=25,
        total_costs_limit=0.0025,
        daily_txs_limit=100,
        leave_balance_on_taiko_chain=0.0011,
        leave_balance_on_source_chains=0.0011,
        taikodrips_stake_amount_range=(0.02, 0.03)
    )
)
