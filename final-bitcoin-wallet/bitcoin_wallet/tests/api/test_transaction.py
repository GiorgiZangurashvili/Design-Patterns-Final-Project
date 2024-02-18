import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from bitcoin_wallet.infra.fastapi.api.api import (
    get_transactions,
    get_wallet_transactions,
    make_transaction,
)


class TestTransactionAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.transactions_mock = MagicMock()

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_make_transaction_success(self, mock_transactions: MagicMock) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1
        from_wallet_id = 1
        to_wallet_id = 2
        amount_transferred = 10.0
        expected_transaction_id = 123

        self.transactions_mock.authorize_transaction.return_value = True
        self.transactions_mock.make_transaction.return_value = expected_transaction_id

        response = make_transaction(
            user_id=user_id,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            amount_transferred=amount_transferred,
            transactions=self.transactions_mock,
        )

        self.assertEqual(response, {"transaction_id": expected_transaction_id})
        self.transactions_mock.authorize_transaction.assert_called_once_with(
            from_wallet_id, user_id
        )
        self.transactions_mock.make_transaction.assert_called_once_with(
            from_wallet_id, to_wallet_id, amount_transferred
        )

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_make_transaction_unauthorized(self, mock_transactions: MagicMock) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1
        from_wallet_id = 1
        to_wallet_id = 2
        amount_transferred = 10.0

        self.transactions_mock.authorize_transaction.return_value = False
        with self.assertRaises(HTTPException):
            make_transaction(
                user_id=user_id,
                from_wallet_id=from_wallet_id,
                to_wallet_id=to_wallet_id,
                amount_transferred=amount_transferred,
                transactions=self.transactions_mock,
            )
        self.transactions_mock.authorize_transaction.assert_called_once_with(
            from_wallet_id, user_id
        )
        self.transactions_mock.make_transaction.assert_not_called()

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_get_transactions_success(self, mock_transactions: MagicMock) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1
        expected_user_transactions = [
            MagicMock(
                id=1,
                from_wallet_id=1,
                to_wallet_id=2,
                amount_transferred=10.0,
                lost_amount=0.0,
            ),
            MagicMock(
                id=2,
                from_wallet_id=2,
                to_wallet_id=3,
                amount_transferred=5.0,
                lost_amount=0.0,
            ),
        ]

        self.transactions_mock.get_user_transactions.return_value = (
            expected_user_transactions
        )

        response = get_transactions(
            user_id=user_id, transactions=self.transactions_mock
        )

        self.assertEqual(
            response,
            [
                {
                    "transaction_id": 1,
                    "from_wallet_id": 1,
                    "to_wallet_id": 2,
                    "amount_transferred": 10.0,
                    "lost_amount": 0.0,
                },
                {
                    "transaction_id": 2,
                    "from_wallet_id": 2,
                    "to_wallet_id": 3,
                    "amount_transferred": 5.0,
                    "lost_amount": 0.0,
                },
            ],
        )
        self.transactions_mock.get_user_transactions.assert_called_once_with(user_id)

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_get_transactions_exception(self, mock_transactions: MagicMock) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1

        self.transactions_mock.get_user_transactions.side_effect = Exception(
            "Test exception"
        )

        with self.assertRaises(HTTPException) as context:
            get_transactions(user_id=user_id, transactions=self.transactions_mock)

        self.assertEqual(context.exception.status_code, 400)
        self.transactions_mock.get_user_transactions.assert_called_once_with(user_id)

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_get_wallet_transactions_success(
        self, mock_transactions: MagicMock
    ) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1
        address = 2
        expected_wallet_transactions = [
            MagicMock(
                id=1,
                from_wallet_id=2,
                to_wallet_id=3,
                amount_transferred=5.0,
                lost_amount=0.0,
            ),
            MagicMock(
                id=2,
                from_wallet_id=3,
                to_wallet_id=4,
                amount_transferred=8.0,
                lost_amount=0.0,
            ),
        ]

        self.transactions_mock.authorize_transaction.return_value = True
        self.transactions_mock.get_wallet_transactions.return_value = (
            expected_wallet_transactions
        )

        # Test
        response = get_wallet_transactions(
            address=address, user_id=user_id, transactions=self.transactions_mock
        )

        self.assertEqual(
            response,
            [
                {
                    "transaction_id": 1,
                    "from_wallet_id": 2,
                    "to_wallet_id": 3,
                    "amount_transferred": 5.0,
                    "lost_amount": 0.0,
                },
                {
                    "transaction_id": 2,
                    "from_wallet_id": 3,
                    "to_wallet_id": 4,
                    "amount_transferred": 8.0,
                    "lost_amount": 0.0,
                },
            ],
        )
        self.transactions_mock.authorize_transaction.assert_called_once_with(
            address, user_id
        )
        self.transactions_mock.get_wallet_transactions.assert_called_once_with(address)

    @patch(
        "bitcoin_wallet.infra.fastapi.dependable."
        "transaction_repository.TransactionRepositoryDependable",
        autospec=True,
    )
    def test_get_wallet_transactions_unauthorized(
        self, mock_transactions: MagicMock
    ) -> None:
        mock_transactions.return_value = self.transactions_mock
        user_id = 1
        address = 2

        self.transactions_mock.authorize_transaction.return_value = False

        with self.assertRaises(HTTPException):
            get_wallet_transactions(
                address=address, user_id=user_id, transactions=self.transactions_mock
            )

        self.transactions_mock.authorize_transaction.assert_called_once_with(
            address, user_id
        )
        self.transactions_mock.get_wallet_transactions.assert_not_called()


if __name__ == "__main__":
    unittest.main()
