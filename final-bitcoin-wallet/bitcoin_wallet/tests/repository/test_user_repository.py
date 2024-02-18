import unittest

from bitcoin_wallet.core.config.constants import USER_DEFAULT_ID
from bitcoin_wallet.core.entity.user import BtcUser
from bitcoin_wallet.core.exception.mail_already_present import (
    MailAlreadyPresentException,
)
from bitcoin_wallet.core.exception.mail_not_valid import MailNotValidException
from bitcoin_wallet.core.exception.no_more_wallets import NoMoreWalletsLeftException
from bitcoin_wallet.core.exception.user_not_found import UserNotFoundException
from bitcoin_wallet.core.exception.wallet_already_present import (
    WalletAlreadyPresentException,
)
from bitcoin_wallet.core.repository.user_repository import BtcUserRepository
from bitcoin_wallet.tests.repository.setup import SetupForTests


class TestUserRepository(unittest.TestCase):
    def setUp(self) -> None:
        db_filename: str = "test_users.db"
        self.repository = BtcUserRepository(db_file=db_filename)
        self.repository.filename = db_filename
        SetupForTests.create_tables(db_filename)

    def test_create_user(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test1@gmail.com")
        id: int = self.repository.create(btc_user)
        self.assertEqual(id, 1)

    def test_create_user_throws_mail_exists_exception(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test2@gmail.com")
        id: int = self.repository.create(btc_user)
        self.assertEqual(id, 1)

        # trying to create user with existing mail
        self.assertRaises(MailAlreadyPresentException, self.repository.create, btc_user)

    def test_create_user_throws_mail_invalid_format_exception(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="invalid_gmail.co")

        # trying to create user with invalid mail
        self.assertRaises(MailNotValidException, self.repository.create, btc_user)

    def test_read(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test3@gmail.com")
        id: int = self.repository.create(btc_user)
        self.assertEqual(id, 1)

        read_user = self.repository.read(1)
        self.assertEqual(read_user.mail, "test3@gmail.com")

    def test_read_throws_exception(self) -> None:
        self.assertRaises(UserNotFoundException, self.repository.read, 1)

    def test_read_all(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test4@gmail.com")
        first_id: int = self.repository.create(btc_user)
        self.assertEqual(first_id, 1)
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test5@gmail.com")
        second_id: int = self.repository.create(btc_user)
        self.assertEqual(second_id, 2)
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test6@gmail.com")
        third_id: int = self.repository.create(btc_user)
        self.assertEqual(third_id, 3)

        self.assertEqual(len(self.repository.read_all()), 3)

    def test_register_new_wallet(self) -> None:
        btc_user = BtcUser(id=USER_DEFAULT_ID, mail="test4@gmail.com")
        first_id: int = self.repository.create(btc_user)
        self.assertEqual(first_id, 1)
        self.repository.register_new_wallet(1, 1)
        self.repository.register_new_wallet(1, 2)
        self.assertRaises(
            WalletAlreadyPresentException, self.repository.register_new_wallet, 1, 2
        )
        self.repository.register_new_wallet(1, 3)
        self.assertRaises(
            NoMoreWalletsLeftException, self.repository.register_new_wallet, 1, 4
        )
        self.assertRaises(
            UserNotFoundException, self.repository.register_new_wallet, 2, 1
        )


if __name__ == "__main__":
    unittest.main()
