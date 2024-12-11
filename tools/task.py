import random

from datatypes.account import AccountItem
from modules.allowance import random_allowance_main
from modules.blazplay import blazplay_main
from modules.brigade import brigade_main
from modules.conft import conft_mint
from modules.contract import contract_deploy
from modules.crack_x_stack import crack_x_stack_main
from modules.gas_zip import gas_zip_bridge
from modules.hana import hana_with_borrow_main, hana_main
from modules.hyperlane import hyperlane_bridge
from modules.kiloex import kiloex_main
from modules.meridians import meridian_usdc_main, meridian_usdc_withdraw_main, meridian_main
from modules.omnihub import omnihub_mint
from modules.openalchi import openalchi_standart_mint
from modules.orbiter import orbiter_bridge
from modules.owlto import owlto_deploy_main
from modules.oxastra import oxastra_checkin
from modules.relay import relay_bridge
from modules.rhino import rhino_gm, rhino_deploy_main
from modules.rubyscore import rubyscore_vote
from modules.taikodrips import taikodrips_main
from modules.transfer import self_transfer_main, burner_transfer_main
from modules.wrap import wrap_main
from modules.xy import xy_bridge
from modules.zypher2048 import zypher2048_main
from sdk.sql import SQL
from user_data.chains import source_chains, taiko_chain, destination_chains


def bridge_deposit(sql: SQL, acc: AccountItem, today: str):
    random.shuffle(source_chains)
    for chain in source_chains:
        bridge_to_use = random.choice(acc.config.common.bridges_to_use)
        if 'orbiter' in bridge_to_use:
            orbiter_bridge(
                account_item=acc,
                source_chain=chain,
                recipient_chain=taiko_chain,
                day=today,
                sql=sql,
                multiplier_range=(0.91, 1),
                minimum_transfer=acc.config.common.minimum_transfer_value
            )
        elif 'xy' in bridge_to_use:
            xy_bridge(
                account_item=acc,
                source_chain=chain,
                recipient_chain=taiko_chain,
                day=today,
                sql=sql,
                multiplier_range=(0.91, 1),
                minimum_transfer=acc.config.common.minimum_transfer_value
            )
        elif 'relay' in bridge_to_use:
            relay_bridge(
                account_item=acc,
                source_chain=chain,
                recipient_chain=taiko_chain,
                day=today,
                sql=sql,
                multiplier_range=(0.91, 1),
                minimum_transfer=acc.config.common.minimum_transfer_value
            )
        elif 'hyperlane' in bridge_to_use:
            hyperlane_bridge(
                account_item=acc,
                source_chain=chain,
                recipient_chain=taiko_chain,
                day=today,
                sql=sql,
                multiplier_range=(0.91, 1),
                minimum_transfer=acc.config.common.minimum_transfer_value
            )
        elif 'gas.zip' in bridge_to_use:
            gas_zip_bridge(
                account_item=acc,
                source_chain=chain,
                recipient_chain=taiko_chain,
                day=today,
                sql=sql,
                multiplier_range=(0.91, 1),
                minimum_transfer=acc.config.common.minimum_transfer_value
            )


def bridge_withdraw(sql: SQL, acc: AccountItem, today: str):
    bridge_to_use = random.choice(acc.config.common.bridges_to_use)
    if 'orbiter' in bridge_to_use:
        orbiter_bridge(
            account_item=acc,
            source_chain=taiko_chain,
            recipient_chain=random.choice(destination_chains),
            day=today,
            sql=sql,
            multiplier_range=(0.91, 1),
            minimum_transfer=acc.config.common.minimum_transfer_value
        )
    elif 'xy' in bridge_to_use:
        xy_bridge(
            account_item=acc,
            source_chain=taiko_chain,
            recipient_chain=random.choice(destination_chains),
            day=today,
            sql=sql,
            multiplier_range=(0.91, 1),
            minimum_transfer=acc.config.common.minimum_transfer_value
        )
    elif 'relay' in bridge_to_use:
        relay_bridge(
            account_item=acc,
            source_chain=taiko_chain,
            recipient_chain=random.choice(destination_chains),
            day=today,
            sql=sql,
            multiplier_range=(0.91, 1),
            minimum_transfer=acc.config.common.minimum_transfer_value
        )
    elif 'hyperlane' in bridge_to_use:
        hyperlane_bridge(
            account_item=acc,
            source_chain=taiko_chain,
            recipient_chain=random.choice(destination_chains),
            day=today,
            sql=sql,
            multiplier_range=(0.91, 1),
            minimum_transfer=acc.config.common.minimum_transfer_value
        )
    elif 'gas.zip' in bridge_to_use:
        gas_zip_bridge(
            account_item=acc,
            source_chain=taiko_chain,
            recipient_chain=random.choice(destination_chains),
            day=today,
            sql=sql,
            multiplier_range=(0.91, 1),
            minimum_transfer=acc.config.common.minimum_transfer_value
        )


def wrap_task(sql: SQL, acc: AccountItem, today: str):
    wrap_main(index=acc.id, private_key=acc.private_key, multiplier_range=(0.5, 0.8))


def unwrap_task(sql: SQL, acc: AccountItem, today: str):
    wrap_main(index=acc.id, private_key=acc.private_key, multiplier_range=(1, 1), unwrap_only=True)


def conft_task(sql: SQL, acc: AccountItem, today: str):
    conft_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def omnihub_task(sql: SQL, acc: AccountItem, today: str):
    omnihub_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def rubyscore_task(sql: SQL, acc: AccountItem, today: str):
    rubyscore_vote(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def rhino_task(sql: SQL, acc: AccountItem, today: str):
    rhino_gm(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def hana_task(sql: SQL, acc: AccountItem, today: str):
    hana_main(
        acc=acc,
        index=acc.id,
        private_key=acc.private_key,
        sql=sql,
        day=today
    )


def hana_withdraw_with_borrow_task(sql: SQL, acc: AccountItem, today: str):
    hana_with_borrow_main(
        acc=acc,
        index=acc.id,
        private_key=acc.private_key,
        sql=sql,
        day=today,
        multiplier_range=(0.91, 0.95),
        only_withdraw=True
    )


def hana_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    hana_main(
        acc=acc,
        index=acc.id,
        private_key=acc.private_key,
        sql=sql,
        day=today,
        only_withdraw=True
    )


def self_transfer_task(sql: SQL, acc: AccountItem, today: str):
    self_transfer_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today, multiplier_range=(0.5, 0.9))


def burner_transfer_task(sql: SQL, acc: AccountItem, today: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(
        index=acc.id,
        main_private_key=acc.private_key,
        burner_private_key=burner_key,
        sql=sql,
        day=today,
        multiplier_range=(0.5, 0.9)
    )


def burner_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(
        index=acc.id,
        main_private_key=acc.private_key,
        burner_private_key=burner_key,
        sql=sql,
        day=today,
        multiplier_range=(0.95, 0.98),
        withdraw_only=True
    )


def brigade_nft_task(sql: SQL, acc: AccountItem, today: str):
    brigade_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def meridian_usdc_task(sql: SQL, acc: AccountItem, today: str):
    meridian_usdc_main(acc=acc, sql=sql, day=today)


def meridian_usdc_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    meridian_usdc_withdraw_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def kiloex_task(sql: SQL, acc: AccountItem, today: str):
    kiloex_main(acc=acc, sql=sql, day=today)


def crack_x_stack_task(sql: SQL, acc: AccountItem, today: str):
    crack_x_stack_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def zypher2048_task(sql: SQL, acc: AccountItem, today: str):
    zypher2048_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def taikodrips_task(sql: SQL, acc: AccountItem, today: str):
    taikodrips_main(account=acc, sql=sql, day=today)


def oxastra_task(sql: SQL, acc: AccountItem, today: str):
    oxastra_checkin(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def contract_task(sql: SQL, acc: AccountItem, today: str):
    contract_deploy(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def rhino_deploy_task(sql: SQL, acc: AccountItem, today: str):
    rhino_deploy_main(
        acc=acc,
        index=acc.id,
        private_key=acc.private_key,
        proxy=acc.proxy,
        sql=sql,
        day=today
    )


def blazplay_task(sql: SQL, acc: AccountItem, today: str):
    blazplay_main(acc=acc, sql=sql, day=today)


def openalchi_task(sql: SQL, acc: AccountItem, today: str):
    openalchi_standart_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def random_allowance_task(sql: SQL, acc: AccountItem, today: str):
    random_allowance_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def meridian_task(sql: SQL, acc: AccountItem, today: str):
    meridian_main(acc=acc, sql=sql, day=today)


def meridian_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    meridian_main(acc=acc, sql=sql, day=today, only_withdraw=True)


def owlto_task(sql: SQL, acc: AccountItem, today: str):
    owlto_deploy_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)
