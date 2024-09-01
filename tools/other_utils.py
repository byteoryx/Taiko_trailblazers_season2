import random
import re
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pydantic
from loguru import logger

from datatypes.collector import CollectorItem


def read_file(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line and not line.startswith('# ')]
    return not_empty


def sleep_in_range(sec_from: int, sec_to: int, log: str = None):
    sleep_time = random.randint(sec_from, sec_to)
    if log:
        logger.info(f"sleep {sleep_time} sec | {log}.")
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


def get_today_bridge() -> str:
    today = datetime.now(timezone.utc).strftime("%B%d")
    return today + 'Bridge'


def get_csv_accs_pd(path: str) -> tuple[pd.DataFrame, list[CollectorItem]]:
    with open(path, 'r', encoding='utf-8') as csv_file:
        df = pd.read_csv(csv_file, dtype=str)
    df = df.replace({np.nan: None})
    df.set_index("id")
    accs = []
    for acc in df.to_dict("records"):
        try:
            accs.append(CollectorItem.parse_obj(acc))
        except pydantic.error_wrappers.ValidationError as ex:
            logger.error(f'[{acc["num"]}] Error importing: {ex}')
    return df, accs


def load_csv_accs_pd(df: pd.DataFrame, path: str):
    df.to_csv(path)
