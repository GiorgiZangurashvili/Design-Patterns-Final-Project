import unittest
from unittest.mock import MagicMock

from fastapi import HTTPException

from bitcoin_wallet.core.exception.mail_already_present import (
    MailAlreadyPresentException,
)
from bitcoin_wallet.infra.fastapi.api.api import create_user
from bitcoin_wallet.infra.fastapi.request.create_user_request import CreateUserRequest


class TestCreateUser(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_user_repository = MagicMock()

    def test_create_user_success(self) -> None:
        request = CreateUserRequest(mail="test@gmail.com")
        self.mock_user_repository.create.return_value = 3
        response = create_user(request, self.mock_user_repository)
        self.assertEqual(response, {"api_key": 3})

    def test_create_user_mail_already_present_exception(self) -> None:
        existing_mail: str = "mailalreadyexists@gmail.com"
        request = CreateUserRequest(mail=existing_mail)
        self.mock_user_repository.create.side_effect = MailAlreadyPresentException(
            existing_mail
        )
        with self.assertRaises(HTTPException) as cm:
            create_user(request, self.mock_user_repository)
        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(
            cm.exception.detail, "Mail that you have provided is already registered"
        )


if __name__ == "__main__":
    unittest.main()
