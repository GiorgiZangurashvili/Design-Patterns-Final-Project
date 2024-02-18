import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from bitcoin_wallet.core.exception.no_more_wallets import NoMoreWalletsLeftException
from bitcoin_wallet.core.repository.wallet_repository import BtcWalletRepository


class TestBtcWalletRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db_file = "/tests/repository/test_wallet.db"
        self.repo = BtcWalletRepository(db_file=self.db_file)

    def tearDown(self) -> None:
        try:
            with open(self.db_file, "r") as f:
                f.close()
        except FileNotFoundError:
            pass

    def test_setup(self) -> None:
        self.repo.setup()

    @patch("sqlite3.connect")
    def test_authorize_user_valid_user(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.return_value = (
            1,
            "username",
            0,
            0,
            0,
        )
        mock_connect.return_value.cursor.return_value = mock_cursor

        result = self.repo.authorize_user(user_id=1)
        self.assertTrue(result)

    @patch("sqlite3.connect")
    def test_authorize_user_should_return_true(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.return_value = (
            150,
            "username",
            0,
            0,
            0,
        )
        mock_connect.return_value.cursor.return_value = mock_cursor

        result = self.repo.authorize_user(user_id=150)

        self.assertTrue(result)

    @patch("sqlite3.connect")
    def test_create_wallet_user_not_found(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.return_value = None
        mock_connect.return_value.cursor.return_value = mock_cursor

        with self.assertRaises(NoMoreWalletsLeftException):
            self.repo.create_wallet(user_id=1, initial_balance=10)

    @patch("sqlite3.connect")
    def test_retrieve_wallet_info_user_no_access(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.side_effect = [
            (1, "username", 1, 2, 3),
            (1, 10),
        ]
        mock_connect.return_value.cursor.return_value = mock_cursor

        with self.assertRaises(HTTPException):
            self.repo.retrieve_wallet_info(user_id=1, wallet_id=2)

    @patch("sqlite3.connect")
    def test_create_wallet_max_wallets(self, mock_connect: MagicMock) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.return_value = (
            1,
            "username",
            1,
            2,
            3,
        )
        mock_connect.return_value.cursor.return_value = mock_cursor

        with self.assertRaises(NoMoreWalletsLeftException):
            self.repo.create_wallet(user_id=1, initial_balance=10)

    @patch("sqlite3.connect")
    def test_retrieve_wallet_info_persmission_error(
        self, mock_connect: MagicMock
    ) -> None:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value.fetchone.side_effect = [
            (1, "username", 1, 2, 3),
            None,
        ]
        mock_connect.return_value.cursor.return_value = mock_cursor

        with self.assertRaises(HTTPException) as context:
            self.repo.retrieve_wallet_info(user_id=1, wallet_id=5)

        self.assertEqual(context.exception.status_code, 405)


if __name__ == "__main__":
    unittest.main()
