import sqlite3
import pandas as pd
import re
from loguru import logger

from data.constants import database_path, csv_path
from tools.add_logger import add_logger


def calculate_total_staked(stakes):
    if pd.isna(stakes):
        return 0.0

    values = map(float, re.findall(r'\d+\.\d+', stakes))
    return sum(values)


def export():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    accs_df = pd.read_sql_query("SELECT * FROM accs", conn)

    if 'last_edited' in accs_df.columns:
        accs_df = accs_df.drop(columns=['last_edited'])

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        if table_name != 'accs' and 'Report' not in table_name:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

            if 'last_edited' in df.columns:
                df = df.drop(columns=['last_edited'])

            if 'id' in df.columns:
                accs_df = pd.merge(accs_df, df, on="id", how="left", suffixes=('', f'_{table_name}'))

    if 'stakes' in accs_df.columns:
        accs_df['total_staked'] = accs_df['stakes'].apply(calculate_total_staked)

    accs_df.to_csv(csv_path, index=False)
    print(f"'{database_path}' has been exported into '{csv_path}'.")

    conn.close()


if __name__ == '__main__':
    add_logger()
    try:
        export()
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        logger.exception(e)
