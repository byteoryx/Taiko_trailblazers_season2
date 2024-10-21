import random
import re
import time
from datetime import datetime, timezone

from loguru import logger

from user_data.tiers import tier_collection


def read_file(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line and not line.startswith('# ')]
    return not_empty


def sleep_in_range(sec_from: int, sec_to: int, log: str = None):
    sleep_time = random.randint(sec_from, sec_to)
    if log:
        logger.info(f"sleep {round(sleep_time, 2)} sec | {log}.")
    time.sleep(sleep_time)


def extract_rhino_contracts(path: str):
    addresses = []
    pattern = re.compile(r'0x[a-fA-F0-9]{40}')

    with open(path, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                addresses.append(match.group())

    return addresses


def get_today_table_name() -> str:
    today = datetime.now(timezone.utc).strftime("%B%d")
    return today + 'Report'


def get_leave_on_source(tier: str, chain: str):
    chain_field = "leave_balance_on_taiko_chain" if chain == "taiko" else "leave_balance_on_source_chains"

    tier_obj = getattr(tier_collection, tier)
    leave_on_source = getattr(tier_obj, chain_field)

    return leave_on_source


def get_stake_limits(tier: str):
    tier_obj = getattr(tier_collection, tier)
    stake_limit = getattr(tier_obj, 'taikodrips_stake_amount_range')

    return stake_limit
