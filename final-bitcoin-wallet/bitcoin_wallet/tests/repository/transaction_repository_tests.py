import sqlite3
import unittest

from bitcoin_wallet.core.repository.transaction_repository import (
    BtcTransactionRepository,
)
from bitcoin_wallet.tests.repository.setup import SetupForTests


class TestBtcTransactionRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect("test_transaction.db")
        self.repository = BtcTransactionRepository(
            db_file="/tests/repository/test_transaction.db"
        )
        SetupForTests.create_tables("test_transaction.db")
        self._create_test_data()

    def tearDown(self) -> None:
        self.connection.close()

    def _create_test_data(self) -> None:
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (id, first_wallet_id) VALUES (1, 1)")
            cursor.execute("INSERT INTO users (id, first_wallet_id) VALUES (2, 2)")
            cursor.execute(
                "INSERT INTO wallets (id, user_id, balance) VALUES (1, 1, 100)"
            )
            cursor.execute(
                "INSERT INTO wallets (id, user_id, balance) VALUES (2, 2, 100)"
            )

    def test_make_transaction(self) -> None:
        transaction_id = self.repository.make_transaction(1, 2, 10.0)
        self.assertIsNotNone(transaction_id)

    def test_get_user_transactions(self) -> None:
        self.repository.make_transaction(1, 2, 10.0)
        transactions = self.repository.get_user_transactions(1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].from_wallet_id, 1)
        self.assertEqual(transactions[0].to_wallet_id, 2)

    def test_get_wallet_transactions(self) -> None:
        self.repository.make_transaction(1, 2, 10.0)
        transactions = self.repository.get_wallet_transactions(1)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].from_wallet_id, 1)
        self.assertEqual(transactions[0].to_wallet_id, 2)

    def test_authorize_transaction(self) -> None:
        authorized = self.repository.authorize_transaction(1, 1)
        self.assertTrue(authorized)
        authorized = self.repository.authorize_transaction(1, 2)
        self.assertFalse(authorized)

    def test_read_all(self) -> None:
        self.repository.make_transaction(1, 2, 10.0)
        self.repository.make_transaction(2, 1, 5.0)
        transactions = self.repository.read_all()
        self.assertEqual(len(transactions), 2)


if __name__ == "__main__":
    unittest.main()
