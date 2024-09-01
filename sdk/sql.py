import sqlite3

from datatypes.account import AccountItem, DayBridgeItem, TrailblazersItem, BurnerItem, BadgeItem


class SQL:
    def __init__(self, database: str = rf"../data/data.db"):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.accs_table = 'accs'
        self.trailblazers_table = 'trailblazers'
        self.burner_table = 'burner'
        self.create_acc_table()
        self.create_trailblazers_table()
        self.create_burner_table()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def fetch_all(self, table: str):
        with self.connection:
            result = self.connection.cursor().execute(f"SELECT * FROM {table}").fetchall()
            return result

    def fetch_all_by_owner(self, table: str, owner: str):
        with self.connection:
            result = self.connection.cursor().execute(f"SELECT * FROM {table} WHERE owner = '{owner}'").fetchall()
            return result

    def fetch_not_minted_badge(self, badge_id: int):
        query = f"""
                    SELECT acc.*
                    FROM accs acc
                    LEFT JOIN badge{badge_id} b ON acc.id = b.id
                    WHERE b.id IS NULL OR COALESCE(b.minted, 'False') != 'True'
                """

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        return results

    def fetch_row(self, table: str, param: str, value, string: bool = True):
        if string:
            with self.connection:
                result = self.connection.cursor().execute(f"SELECT * FROM {table} where {param} = '{value}'").fetchall()
                return result
        else:
            with self.connection:
                result = self.connection.cursor().execute(f"SELECT * FROM {table} where {param} = {value}").fetchall()
                return result

    def is_row_exist(self, table: str, param: str, value, string: bool = True):
        if string:
            with self.connection:
                fetch = self.connection.cursor().execute(
                    f"SELECT * FROM {table} where {param} = '{value}'").fetchall()

                return True if len(fetch) > 0 else False
        else:
            with self.connection:
                fetch = self.connection.cursor().execute(
                    f"SELECT * FROM {table} where {param} = {value}").fetchall()

                return True if len(fetch) > 0 else False

    def add_badge_report(self, badge_id: int, badge_item: BadgeItem, acc_id: int):
        status = ""
        table = f'badge{badge_id}'
        exists = self.is_row_exist(table=table, param='id', value=acc_id)

        with self.connection:
            cursor = self.connection.cursor()

            if exists:
                cursor.execute(f"SELECT minted FROM {table} WHERE id = ?", (acc_id,))
                current_nft_minted = cursor.fetchone()[0]

                if current_nft_minted != badge_item.minted:
                    cursor.execute(f"UPDATE {table} "
                                   f"SET minted = ?, last_edited = ? WHERE id = ?",
                                   (badge_item.minted, badge_item.last_edited, acc_id))
                    status = f"updated: {current_nft_minted if current_nft_minted else 'None'} > {badge_item.minted}"
                    self.commit()
            else:
                cursor.execute(f"INSERT INTO {table} "
                               f"(id, minted, last_edited) "
                               f"VALUES (?, ?, ?)",
                               (acc_id, badge_item.minted, badge_item.last_edited))
                status = "inserted"

                self.commit()

        return status

    def update_badges(self, acc: AccountItem, badges: str, count: int):
        string = f'{count}: {badges}'
        status = ""

        with self.connection:
            cursor = self.connection.cursor()

            cursor.execute(f'SELECT badge_ids FROM {self.trailblazers_table} WHERE id = ?', (acc.id,))
            current_badge_ids = cursor.fetchone()

            if current_badge_ids:
                current_badge_ids = current_badge_ids[0]

                if current_badge_ids != string:
                    cursor.execute(f'''
                        UPDATE {self.trailblazers_table}
                        SET badge_ids = ?
                        WHERE id = ?
                    ''', (string, acc.id))
                    status = f"updated: {current_badge_ids if current_badge_ids else 'no badges'} > {string}"
                    self.commit()
            else:
                cursor.execute(f'''
                    INSERT INTO {self.trailblazers_table} (id, badge_ids)
                    VALUES (?, ?)
                ''', (acc.id, string))
                status = "inserted"
                self.commit()

        return status

    def get_owned_badges(self, id: int):
        with self.connection:
            result = self.connection.cursor().execute(f'SELECT badge_ids FROM {self.trailblazers_table} WHERE id = ?',
                                                      (id,)).fetchone()
            try:
                return result[0]
            except:
                return ''

    def add_acc(self, acc: AccountItem):
        if not self.is_row_exist(table=self.accs_table, param='private_key', value=acc.private_key):
            with self.connection:
                self.connection.cursor().execute(f"INSERT INTO {self.accs_table} "
                                                 f"(id, private_key, proxy, owner, tier, last_edited) "
                                                 f"VALUES (?, ?, ?, ?, ?, ?)",
                                                 (acc.id, acc.private_key, acc.proxy, acc.owner, acc.tier,
                                                  acc.last_edited))
                self.commit()
            return True
        else:
            return False

    def add_burner(self, acc: BurnerItem):
        if not self.is_row_exist(table=self.burner_table, param='id', value=acc.id):
            with self.connection:
                self.connection.cursor().execute(f"INSERT INTO {self.burner_table} "
                                                 f"(id, private_key, last_edited) "
                                                 f"VALUES (?, ?, ?)",
                                                 (acc.id, acc.private_key, acc.last_edited))
                self.commit()
            return True
        else:
            return False

    def get_volume_and_txs_by_id(self, day: str, acc_id: int):
        with self.connection:
            cursor = self.connection.cursor()
            query = f"""
                SELECT 
                    COALESCE(volume, 0), 
                    COALESCE(txs, 0), 
                    COALESCE(costs, 0) 
                FROM {day} 
                WHERE id = ?
            """

            cursor.execute(query, (acc_id,))
            result = cursor.fetchone()

            if result:
                volume, txs, costs = result
                return volume, txs, costs
            else:
                return 0, 0, 0

    def get_burner_by_id(self, acc_id: int):
        with self.connection:
            cursor = self.connection.cursor()
            query = f"""
                SELECT 
                    private_key
                FROM {self.burner_table} 
                WHERE id = ?
            """

            cursor.execute(query, (acc_id,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return ''

    def add_bridge_day_report(self, day_item: DayBridgeItem, day: str, acc_id: int):
        status = ""

        exists = self.is_row_exist(table=day, param='id', value=acc_id)

        with self.connection:
            cursor = self.connection.cursor()

            if exists:
                cursor.execute(f"SELECT volume FROM {day} WHERE id = ?", (acc_id,))
                current_volume = cursor.fetchone()[0]

                cursor.execute(f"SELECT txs FROM {day} WHERE id = ?", (acc_id,))
                current_txs = cursor.fetchone()[0]

                cursor.execute(f"SELECT costs FROM {day} WHERE id = ?", (acc_id,))
                current_costs = cursor.fetchone()[0]

                if current_costs != day_item.costs:
                    if day_item.volume >= 0 and 0 <= day_item.costs < 0.01:
                        cursor.execute(f"UPDATE {day} "
                                       f"SET volume = ?, txs = ?, costs = ?, last_edited = ? WHERE id = ?",
                                       (day_item.volume, day_item.txs, day_item.costs, day_item.last_edited, acc_id))
                        status = f"daily costs updated: {round(current_costs, 6)} > {round(day_item.costs, 6)}"
                        self.commit()
                    else:
                        status = f'{day_item.volume=} < 0, {day_item.costs=} > 0.003'
            else:
                if day_item.volume >= 0 and 0 <= day_item.costs < 0.01:
                    cursor.execute(f"INSERT INTO {day} "
                                   f"(id, volume, txs, costs, last_edited) "
                                   f"VALUES (?, ?, ?, ?, ?)",
                                   (acc_id, day_item.volume, day_item.txs, day_item.costs, day_item.last_edited))
                    status = f"costs inserted: 0 > {round(day_item.costs, 6)}"
                    self.commit()
                else:
                    status = f'{day_item.volume=} < 0, {day_item.costs=} > 0.003'

        return status

    def add_trailblazers_report(self, trailblazers: TrailblazersItem):
        status = ""

        exists = self.is_row_exist(table=self.trailblazers_table, param='id', value=trailblazers.id)

        with self.connection:
            cursor = self.connection.cursor()

            if exists:
                cursor.execute(f"SELECT points FROM {self.trailblazers_table} WHERE id = ?", (trailblazers.id,))
                current_points = cursor.fetchone()[0]

                if current_points != trailblazers.points:
                    cursor.execute(f"UPDATE {self.trailblazers_table} "
                                   f"SET domain = ?, badge_ids = ?, galxe_points = ?, points = ?, rank = ?, last_edited = ? WHERE id = ?",
                                   (trailblazers.domain,
                                    trailblazers.badge_ids,
                                    trailblazers.galxe_points,
                                    trailblazers.points,
                                    trailblazers.rank,
                                    trailblazers.last_edited,
                                    trailblazers.id))
                    status = f"updated: {current_points} > {trailblazers.points}"
                    self.commit()
            else:
                cursor.execute(f"INSERT INTO {self.trailblazers_table} "
                               f"(id, domain, badge_ids, galxe_points, points, rank, last_edited) "
                               f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (trailblazers.id,
                                trailblazers.domain,
                                trailblazers.badge_ids,
                                trailblazers.galxe_points,
                                trailblazers.points,
                                trailblazers.rank,
                                trailblazers.last_edited))
                status = "inserted"
                self.commit()

        return status

    def fetch_accounts_with_zero_minted(self, day_index: int):
        joins = []
        conditions = []

        for i in range(day_index + 1):
            joins.append(f"LEFT JOIN day_{i} d{i} ON a.id = d{i}.id")
            conditions.append(f"COALESCE(d{i}.nft_minted, 0) = 0")

        join_clause = " ".join(joins)
        where_clause = " AND ".join(conditions)

        query = f"""
            WITH all_days AS (
                SELECT a.id
                FROM {self.accs_table} a
                {join_clause}
                WHERE {where_clause}
            )
            SELECT a.*
            FROM {self.accs_table} a
            JOIN all_days ad ON a.id = ad.id
        """

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        return results

    def _get_tables_with_keyword(self, keyword: str = "Bridge"):
        with self.connection:
            cursor = self.connection.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?"
            cursor.execute(query, (f"%{keyword}%",))
            tables = cursor.fetchall()
            return [table[0] for table in tables]

    def get_total_costs(self, acc_id: int):
        tables = self._get_tables_with_keyword()
        total_costs = 0
        total_volume = 0

        for table in tables:
            with self.connection:
                cursor = self.connection.cursor()
                query = f"""
                    SELECT 
                        COALESCE(SUM(costs), 0), 
                        COALESCE(SUM(volume), 0) 
                    FROM {table}
                    WHERE id = ?
                """
                cursor.execute(query, (acc_id,))
                result = cursor.fetchone()

                if result:
                    total_costs += result[0]
                    total_volume += result[1]

        return total_costs

    def get_today_txs(self, day: str, acc_id: int):
        with self.connection:
            cursor = self.connection.cursor()
            query = f"SELECT txs FROM {day} WHERE id = ?"
            cursor.execute(query, (acc_id,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return 0

    def get_today_volume(self, day: str, acc_id: int):
        with self.connection:
            cursor = self.connection.cursor()
            query = f"SELECT volume FROM {day} WHERE id = ?"
            cursor.execute(query, (acc_id,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return 0

    def get_rank(self, acc_id: int):
        with self.connection:
            cursor = self.connection.cursor()
            query = f"SELECT COALESCE(rank, 0) FROM {self.trailblazers_table} WHERE id = ?"
            cursor.execute(query, (acc_id,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return 0

    def create_acc_table(self):
        with self.connection:
            self.connection.cursor().execute(f"""
                CREATE TABLE IF NOT EXISTS {self.accs_table} (
                    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "private_key" TEXT,
                    "proxy" TEXT,
                    "owner" TEXT,
                    "tier" TEXT,
                    "last_edited" TEXT
                )
            """)
            self.connection.commit()

    def create_bridge_day_table(self, day: str):
        with self.connection:
            self.connection.cursor().execute(f"""
                CREATE TABLE IF NOT EXISTS {day} (
                    "id" INTEGER NOT NULL,
                    "txs" INTEGER,
                    "volume" REAL,
                    "costs" REAL,
                    "last_edited" TEXT,
                    PRIMARY KEY("id"),
                    FOREIGN KEY("id") REFERENCES {self.accs_table}("id")
                )
            """)
            self.connection.commit()

    def create_trailblazers_table(self):
        with self.connection:
            self.connection.cursor().execute(f"""
                CREATE TABLE IF NOT EXISTS {self.trailblazers_table} (
                    "id" INTEGER NOT NULL,
                    "domain" TEXT,
                    "badge_ids" TEXT,
                    "galxe_points" INTEGER,
                    "points" INTEGER,
                    "rank" INTEGER,
                    "last_edited" TEXT,
                    PRIMARY KEY("id"),
                    FOREIGN KEY("id") REFERENCES {self.accs_table}("id")
                )
            """)
            self.connection.commit()

    def create_burner_table(self):
        with self.connection:
            self.connection.cursor().execute(f"""
                CREATE TABLE IF NOT EXISTS {self.burner_table} (
                    "id" INTEGER NOT NULL,
                    "private_key" TEXT,
                    "last_edited" TEXT,
                    PRIMARY KEY("id"),
                    FOREIGN KEY("id") REFERENCES {self.accs_table}("id")
                )
            """)
            self.connection.commit()

    def create_badge_table(self, badge_id: int):
        with self.connection:
            self.connection.cursor().execute(f"""
                CREATE TABLE IF NOT EXISTS badge{badge_id} (
                    "id" INTEGER NOT NULL,
                    "minted" TEXT,
                    "last_edited" TEXT,
                    PRIMARY KEY("id"),
                    FOREIGN KEY("id") REFERENCES {self.accs_table}("id")
                )
            """)
            self.connection.commit()
