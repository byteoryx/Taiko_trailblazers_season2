import random

from datatypes.account import AccountItem
from modules.brigade import brigade_mint
from modules.conft import conft_mint
from modules.crack_x_stack import crack_x_stack_main
from modules.hana import hana_main
from modules.kiloex import kiloex_main
from modules.meridians import meridian_main
from modules.omnihub import omnihub_mint
from modules.orbiter import orbiter_bridge
from modules.rhino_gm import rhino_gm
from modules.rubyscore import rubyscore_vote
from modules.transfer import self_transfer_main, burner_transfer_main
from modules.wrap import wrap_main
from modules.xy import xy_bridge
from modules.zypher2048 import zypher2048_main
from sdk.sql import SQL
from settings.chains import source_chains, taiko_chain, destination_chains
from settings.config import minimum_transfer, minimum_withdraw_from_taiko_transfer, bridges_to_use


def bridge_deposit(sql: SQL, acc: AccountItem, today: str):
    random.shuffle(source_chains)
    for chain in source_chains:
        bridge_to_use = random.choice(bridges_to_use)
        if 'orbiter' in bridge_to_use:
            orbiter_bridge(index=acc.id, private_key=acc.private_key, source_chain=chain,
                           recipient_chain=taiko_chain, day=today, sql=sql,
                           multiplier_range=(0.91, 0.95), minimum_transfer=minimum_transfer * 0.8)
        elif 'xy' in bridge_to_use:
            xy_bridge(index=acc.id, private_key=acc.private_key, source_chain=chain,
                      recipient_chain=taiko_chain, day=today, sql=sql,
                      multiplier_range=(0.91, 0.95), minimum_transfer=minimum_transfer * 0.8)


def bridge_withdraw(sql: SQL, acc: AccountItem, today: str):
    bridge_to_use = random.choice(bridges_to_use)
    if 'orbiter' in bridge_to_use:
        orbiter_bridge(index=acc.id, private_key=acc.private_key, source_chain=taiko_chain,
                       recipient_chain=random.choice(destination_chains), day=today, sql=sql,
                       multiplier_range=(1, 1), minimum_transfer=minimum_withdraw_from_taiko_transfer)
    elif 'xy' in bridge_to_use:
        xy_bridge(index=acc.id, private_key=acc.private_key, source_chain=taiko_chain,
                  recipient_chain=random.choice(destination_chains), day=today, sql=sql,
                  multiplier_range=(1, 1), minimum_transfer=minimum_withdraw_from_taiko_transfer)


def wrap_task(sql: SQL, acc: AccountItem, today: str):
    wrap_main(index=acc.id, private_key=acc.private_key, multiplier_range=(0.91, 0.95))


def unwrap_task(sql: SQL, acc: AccountItem, today: str):
    wrap_main(index=acc.id, private_key=acc.private_key, multiplier_range=(0.91, 0.95), unwrap_only=True)


def conft_task(sql: SQL, acc: AccountItem, today: str):
    conft_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def omnihub_task(sql: SQL, acc: AccountItem, today: str):
    omnihub_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def rubyscore_task(sql: SQL, acc: AccountItem, today: str):
    rubyscore_vote(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def rhino_task(sql: SQL, acc: AccountItem, today: str):
    rhino_gm(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def hana_task(sql: SQL, acc: AccountItem, today: str):
    hana_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today, multiplier_range=(0.91, 0.95))


def hana_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    hana_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today, multiplier_range=(0.91, 0.95),
              only_withdraw=True)


def self_transfer_task(sql: SQL, acc: AccountItem, today: str):
    self_transfer_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today, multiplier_range=(0.5, 0.9))


def burner_transfer_task(sql: SQL, acc: AccountItem, today: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(index=acc.id, main_private_key=acc.private_key,
                         burner_private_key=burner_key,
                         sql=sql, day=today, multiplier_range=(0.5, 0.9))


def burner_withdraw_task(sql: SQL, acc: AccountItem, today: str):
    burner_key = sql.get_burner_by_id(acc_id=acc.id)
    burner_transfer_main(index=acc.id, main_private_key=acc.private_key,
                         burner_private_key=burner_key,
                         sql=sql, day=today, multiplier_range=(0.5, 0.9), withdraw_only=True)


def brigade_nft_task(sql: SQL, acc: AccountItem, today: str):
    brigade_mint(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def meridian_task(sql: SQL, acc: AccountItem, today: str):
    meridian_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def kiloex_task(sql: SQL, acc: AccountItem, today: str):
    kiloex_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def crack_x_stack_task(sql: SQL, acc: AccountItem, today: str):
    crack_x_stack_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)


def zypher2048_task(sql: SQL, acc: AccountItem, today: str):
    zypher2048_main(index=acc.id, private_key=acc.private_key, sql=sql, day=today)
