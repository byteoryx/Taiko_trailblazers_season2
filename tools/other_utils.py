import random
import re
import time
from datetime import datetime, timezone

from loguru import logger

from datatypes.account import AccountItem
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


def get_stake_limits(tier: str) -> [float, float]:
    tier_obj = getattr(tier_collection, tier)
    stake_limit = getattr(tier_obj, 'taikodrips_stake_amount_range')

    return stake_limit


def append_to_file_if_not_exists(file_path: str, string: str):
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            if string in contents:
                return
    except FileNotFoundError:
        pass

    try:
        with open(file_path, 'r+') as file:
            file.seek(0, 2)
            if file.tell() > 0:
                file.seek(file.tell() - 1)
                last_char = file.read(1)
                if last_char != '\n':
                    file.write('\n')
    except FileNotFoundError:
        pass

    with open(file_path, 'a') as file:
        file.write(f"{string}\n")


def insert_tier_configs_into_account_items(accounts: [AccountItem]):
    for acc in accounts:
        if acc.tier == 'A':
            acc.config = tier_collection.A
        elif acc.tier == 'B':
            acc.config = tier_collection.B
        else:
            acc.config = tier_collection.C
    return accounts
