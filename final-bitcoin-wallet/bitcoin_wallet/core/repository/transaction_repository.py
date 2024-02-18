import sqlite3
from sqlite3 import Cursor
from typing import List, Optional, Protocol

from bitcoin_wallet.core.entity.transaction import BtcTransaction
from bitcoin_wallet.core.exception.not_enough_balance import NotEnoughBalanceException
from bitcoin_wallet.core.exception.same_transfer_wallets import (
    SameTransferWalletsException,
)
from bitcoin_wallet.core.exception.user_not_found import UserNotFoundException
from bitcoin_wallet.core.path.db_path_handler import DatabasePathHandler


class BaseTransactionRepository(Protocol):
    def make_transaction(
        self, from_wallet_id: int, to_wallet_id: int, amount_transferred: float
    ) -> Optional[int]:
        pass

    def get_user_transactions(self, user_id: int) -> List[BtcTransaction]:
        pass

    def get_wallet_transactions(self, wallet_id: int) -> List[BtcTransaction]:
        pass

    def authorize_transaction(self, from_wallet_id: int, user_id: int) -> bool:
        pass

    def read_all(self) -> list[BtcTransaction]:
        pass


class BtcTransactionRepository(BaseTransactionRepository):
    def __init__(self, db_file: str = "bitcoin_wallet.db") -> None:
        self.db_name = DatabasePathHandler.get_db_path(db_file)

    def make_transaction(
        self, from_wallet_id: int, to_wallet_id: int, amount_transferred: float
    ) -> Optional[int]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM wallets WHERE id IN (?, ?)",
                (from_wallet_id, to_wallet_id),
            )
            user_ids = cursor.fetchall()
            lost_amount = 0.0

            if len(set(user_ids)) != 1:
                lost_amount = amount_transferred * 0.015

            if self._get_wallet_balance(from_wallet_id) < amount_transferred:
                raise NotEnoughBalanceException(from_wallet_id)

            if from_wallet_id == to_wallet_id:
                raise SameTransferWalletsException(
                    from_wallet_id=from_wallet_id, to_wallet_id=to_wallet_id
                )
            new_balance_to = self._get_wallet_balance(to_wallet_id) + amount_transferred
            cursor.execute(
                "UPDATE wallets SET balance = ? WHERE id = ?",
                (new_balance_to, to_wallet_id),
            )

            # Update the balance in the "from" wallet
            new_balance_from = (
                self._get_wallet_balance(from_wallet_id) - amount_transferred
            )
            cursor.execute(
                "UPDATE wallets SET balance = ? WHERE id = ?",
                (new_balance_from, from_wallet_id),
            )

            cursor.execute(
                "INSERT INTO transactions (from_wallet_id, to_wallet_id, "
                "amount_transferred, lost_amount) "
                "VALUES (?, ?, ?, ?)",
                (from_wallet_id, to_wallet_id, amount_transferred, lost_amount),
            )
            transaction_id = cursor.lastrowid
            conn.commit()

            return transaction_id if transaction_id is not None else None

    def _fetch_transactions(self, params: tuple[int, int]) -> List[BtcTransaction]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, from_wallet_id, to_wallet_id, "
                "amount_transferred, lost_amount "
                "FROM transactions WHERE from_wallet_id = ? OR to_wallet_id = ?",
                params,
            )
            rows = cursor.fetchall()
            return [BtcTransaction(*row) for row in rows]

    def _get_wallet_balance(self, wallet_id: int) -> float:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM wallets WHERE id = ?", (wallet_id,))
            current_balance = float(cursor.fetchone()[0])

            return current_balance

    def get_user_transactions(self, user_id: int) -> List[BtcTransaction]:
        user_query = (
            "SELECT first_wallet_id, second_wallet_id, "
            "third_wallet_id FROM users WHERE id = ?"
        )
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(user_query, (user_id,))
            user_wallets = cursor.fetchone()

            if user_wallets:
                user_wallets = [
                    wallet_id for wallet_id in user_wallets if wallet_id is not None
                ]

                if user_wallets:
                    transactions = []
                    for wallet_id in user_wallets:
                        transactions.extend(
                            self._fetch_transactions((wallet_id, wallet_id))
                        )

                    return transactions
                else:
                    raise UserNotFoundException(user_id)
            else:
                raise UserNotFoundException(user_id)

    def get_wallet_transactions(self, wallet_id: int) -> List[BtcTransaction]:
        return self._fetch_transactions((wallet_id, wallet_id))

    def authorize_transaction(self, from_wallet_id: int, user_id: int) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE id = ? AND "
                "(first_wallet_id = ? OR second_wallet_id = ? "
                "OR third_wallet_id = ?)",
                (user_id, from_wallet_id, from_wallet_id, from_wallet_id),
            )
            authorized_user = cursor.fetchone()

            return bool(authorized_user)

    def read_all(self) -> list[BtcTransaction]:
        conn = sqlite3.connect(self.db_name)
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()

        transactions: list[BtcTransaction] = []
        for row in rows:
            transaction = BtcTransaction(*row)
            transactions.append(transaction)
        return transactions
