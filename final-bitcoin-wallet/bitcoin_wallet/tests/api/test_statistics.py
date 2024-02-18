import unittest
from unittest.mock import MagicMock

from fastapi import HTTPException

from bitcoin_wallet.core.config.constants import ADMIN_API_KEY
from bitcoin_wallet.infra.fastapi.api.api import get_transaction_statistics


class TestGetTransactionStatistics(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_transaction_repository = MagicMock()

    def test_get_transaction_statistics_success(self) -> None:
        expected = {"Platform profit": 350.9, "Total number of transactions": 7}
        self.mock_transaction_repository.read_all.return_value = [
            MagicMock(lost_amount=10.0),
            MagicMock(lost_amount=20.0),
            MagicMock(lost_amount=27.7),
            MagicMock(lost_amount=112.55),
            MagicMock(lost_amount=80.05),
            MagicMock(lost_amount=0.6),
            MagicMock(lost_amount=100.0),
        ]
        actual = get_transaction_statistics(
            ADMIN_API_KEY, self.mock_transaction_repository
        )
        self.assertEqual(expected, actual)

    def test_get_transaction_statistics_unauthorized(self) -> None:
        invalid_api_key = "INVALID-KEY"
        with self.assertRaises(HTTPException) as cm:
            get_transaction_statistics(
                invalid_api_key, self.mock_transaction_repository
            )
        self.assertEqual(cm.exception.status_code, 403)
        self.assertEqual(cm.exception.detail, "Unauthorized to do this operation")


if __name__ == "__main__":
    unittest.main()
