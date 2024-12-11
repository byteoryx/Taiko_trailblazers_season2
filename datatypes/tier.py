from typing import List

from pydantic import BaseModel


class ModulesConfig(BaseModel):
    wraps_range: tuple[int, int]
    conft_mint_range: tuple[int, int]
    omnihub_mint_range: tuple[int, int]
    rubyscore_votes_range: tuple[int, int]
    self_transfer_range: tuple[int, int]
    burner_transfer_range: tuple[int, int]
    brigade_game: bool
    crack_x_stack_range: tuple[int, int]
    zypher2048_range: tuple[int, int]
    oxastra_boost: bool
    contract_deploy_range: tuple[int, int]
    blazplay_mint_limit_per_account: tuple[int, int]
    openalchi_mint: bool
    taikodrips_lock_in_days_range: list[int, int]
    rhino_gms_range: tuple[int, int]
    rhino_deploy_limit_per_account: tuple[int, int]
    taikodrips_stake_amount_range: tuple[float, float] | str
    random_allowance_range: tuple[int, int]
    meridian_range: tuple[int, int]
    hana_range: tuple[int, int]
    owlto_range: tuple[int, int]


class CommonConfig(BaseModel):
    leaderboard_top_limit: float
    total_costs_limit: float
    daily_txs_limit: int
    leave_balance_on_taiko_chain: float
    leave_balance_on_source_chains: float
    deposit_from_source_chains_to_taiko: bool
    withdraw_from_taiko_to_recipients_chains: bool
    transfer_from_recipient_chains_to_cex: bool
    bridges_to_use: List[str]
    minimum_transfer_value: float
    minimum_taiko_balance_to_be_used: float


class TierItem(BaseModel):
    common: CommonConfig
    modules: ModulesConfig


class TierCollection(BaseModel):
    A: TierItem
    B: TierItem
    C: TierItem
