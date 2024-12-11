from datatypes.tier import TierCollection, TierItem, ModulesConfig, CommonConfig

tier_collection = TierCollection(
    A=TierItem(
        common=CommonConfig(
            leaderboard_top_limit=1,
            total_costs_limit=0.0075,
            daily_txs_limit=100,
            leave_balance_on_taiko_chain=0.011,
            leave_balance_on_source_chains=0.0011,
            deposit_from_source_chains_to_taiko=True,
            withdraw_from_taiko_to_recipients_chains=False,
            transfer_from_recipient_chains_to_cex=False,
            bridges_to_use=['hyperlane', 'orbiter', 'xy', 'gas.zip'],
            minimum_transfer_value=0.001,
            minimum_taiko_balance_to_be_used=0.0001
        ),
        modules=ModulesConfig(
            wraps_range=(0, 0),
            conft_mint_range=(0, 0),
            omnihub_mint_range=(0, 0),
            rubyscore_votes_range=(0, 0),
            self_transfer_range=(0, 0),
            burner_transfer_range=(0, 0),
            brigade_game=False,
            crack_x_stack_range=(0, 0),
            zypher2048_range=(0, 0),
            oxastra_boost=False,
            contract_deploy_range=(0, 0),
            blazplay_mint_limit_per_account=(0, 0),
            openalchi_mint=False,
            taikodrips_lock_in_days_range=[60, 91, 182, 365],
            taikodrips_stake_amount_range=(0, 0),
            rhino_gms_range=(0, 0),
            rhino_deploy_limit_per_account=(0, 0),
            random_allowance_range=(0, 0),
            meridian_range=(0, 0),
            hana_range=(0, 0),
            owlto_range=(0, 0)
        )
    ),
    B=TierItem(
        common=CommonConfig(
            leaderboard_top_limit=5,
            total_costs_limit=0.005,
            daily_txs_limit=75,
            leave_balance_on_taiko_chain=0.0051,
            leave_balance_on_source_chains=0.0011,
            deposit_from_source_chains_to_taiko=True,
            withdraw_from_taiko_to_recipients_chains=False,
            transfer_from_recipient_chains_to_cex=False,
            bridges_to_use=['hyperlane', 'gas.zip', 'xy'],
            minimum_transfer_value=0.001,
            minimum_taiko_balance_to_be_used=0.0001
        ),
        modules=ModulesConfig(
            wraps_range=(0, 0),
            conft_mint_range=(0, 0),
            omnihub_mint_range=(0, 0),
            rubyscore_votes_range=(0, 0),
            self_transfer_range=(0, 0),
            burner_transfer_range=(0, 0),
            brigade_game=False,
            crack_x_stack_range=(0, 0),
            zypher2048_range=(0, 0),
            oxastra_boost=False,
            contract_deploy_range=(0, 0),
            blazplay_mint_limit_per_account=(0, 0),
            openalchi_mint=False,
            taikodrips_lock_in_days_range=[60, 91, 182, 365],
            taikodrips_stake_amount_range=(0, 0),
            rhino_gms_range=(0, 0),
            rhino_deploy_limit_per_account=(0, 0),
            random_allowance_range=(0, 0),
            meridian_range=(0, 0),
            hana_range=(0, 0),
            owlto_range=(0, 0)
        )
    ),
    C=TierItem(
        common=CommonConfig(
            leaderboard_top_limit=25,
            total_costs_limit=0.0025,
            daily_txs_limit=50,
            leave_balance_on_taiko_chain=0.0011,
            leave_balance_on_source_chains=0.0011,
            deposit_from_source_chains_to_taiko=True,
            withdraw_from_taiko_to_recipients_chains=False,
            transfer_from_recipient_chains_to_cex=False,
            bridges_to_use=['hyperlane', 'gas.zip'],
            minimum_transfer_value=0.001,
            minimum_taiko_balance_to_be_used=0.0001
        ),
        modules=ModulesConfig(
            wraps_range=(0, 0),
            conft_mint_range=(0, 0),
            omnihub_mint_range=(0, 0),
            rubyscore_votes_range=(0, 0),
            self_transfer_range=(0, 0),
            burner_transfer_range=(0, 0),
            brigade_game=False,
            crack_x_stack_range=(0, 0),
            zypher2048_range=(0, 0),
            oxastra_boost=False,
            contract_deploy_range=(0, 0),
            blazplay_mint_limit_per_account=(0, 0),
            openalchi_mint=False,
            taikodrips_lock_in_days_range=[60, 91, 182, 365],
            taikodrips_stake_amount_range=(0, 0),
            rhino_gms_range=(0, 0),
            rhino_deploy_limit_per_account=(0, 0),
            random_allowance_range=(0, 0),
            meridian_range=(0, 0),
            hana_range=(0, 0),
            owlto_range=(0, 0)
        )
    )
)
