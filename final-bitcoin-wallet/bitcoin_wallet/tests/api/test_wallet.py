import unittest
from unittest.mock import MagicMock

from fastapi import HTTPException

from bitcoin_wallet.core.dto.wallet_dto import WalletDTO
from bitcoin_wallet.infra.fastapi.api.api import create_wallet, get_wallet_info
from bitcoin_wallet.infra.fastapi.request.create_wallet_request import (
    CreateWalletRequest,
)


class TestCreateWallet(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_wallet_repository = MagicMock()

    def test_create_wallet_success(self) -> None:
        request = CreateWalletRequest(user_id=1, initial_balance=5)
        self.mock_wallet_repository.authorize_user.return_value = True
        self.mock_wallet_repository.create_wallet.return_value = WalletDTO(
            wallet_id=1, balance_in_btc=5, balance_in_usd=15
        )
        response = create_wallet(request, self.mock_wallet_repository)
        self.assertEqual(
            response, {"wallet_id": 1, "balance_in_btc": 5, "balance_in_usd": 15}
        )

    def test_create_wallet_authorise_exception(self) -> None:
        request = CreateWalletRequest(user_id=1, initial_balance=5)
        self.mock_wallet_repository.authorize_user.return_value = False
        with self.assertRaises(HTTPException) as cm:
            create_wallet(request, self.mock_wallet_repository)
        self.assertEqual(cm.exception.status_code, 404)

    def test_get_wallet_info_success(self) -> None:
        user_id = 1
        wallet_id = 1
        self.mock_wallet_repository.authorize_user.return_value = True
        self.mock_wallet_repository.retrieve_wallet_info.return_value = WalletDTO(
            wallet_id=1, balance_in_btc=5, balance_in_usd=15
        )

        response = get_wallet_info(user_id, wallet_id, self.mock_wallet_repository)
        self.assertEqual(
            response, {"wallet_id": 1, "balance_in_btc": 5, "balance_in_usd": 15}
        )

    def test_get_wallet_info_authorise_exception(self) -> None:
        user_id = 1
        wallet_id = 1
        self.mock_wallet_repository.authorize_user.return_value = False
        with self.assertRaises(HTTPException) as cm:
            get_wallet_info(user_id, wallet_id, self.mock_wallet_repository)
        self.assertEqual(cm.exception.status_code, 404)

    def test_get_wallet_info_not_found_exception(self) -> None:
        user_id = 1
        wallet_id = 1
        self.mock_wallet_repository.authorize_user.return_value = True
        self.mock_wallet_repository.retrieve_wallet_info.return_value = None
        with self.assertRaises(HTTPException) as cm:
            get_wallet_info(user_id, wallet_id, self.mock_wallet_repository)
        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual(cm.exception.detail, "Wallet not found")


if __name__ == "__main__":
    unittest.main()
