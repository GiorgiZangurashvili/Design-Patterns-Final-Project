import sqlite3


class SetupForTests:
    @staticmethod
    def create_tables(db_name: str) -> None:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS wallets")
        cursor.execute("DROP TABLE IF EXISTS users")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                mail TEXT,
                first_wallet_id INTEGER DEFAULT 0,
                second_wallet_id INTEGER DEFAULT 0,
                third_wallet_id INTEGER DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                balance REAL DEFAULT 1
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                from_wallet_id INTEGER,
                to_wallet_id INTEGER,
                amount_transferred REAL DEFAULT 0.0,
                lost_amount REAL DEFAULT 0.0
            )
            """
        )
