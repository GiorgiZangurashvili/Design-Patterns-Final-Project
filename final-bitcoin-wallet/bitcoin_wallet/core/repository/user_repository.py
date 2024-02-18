import sqlite3
from sqlite3 import Cursor
from typing import Protocol, cast

from bitcoin_wallet.core.entity.user import BaseUser, BtcUser
from bitcoin_wallet.core.exception.mail_already_present import (
    MailAlreadyPresentException,
)
from bitcoin_wallet.core.exception.mail_not_valid import MailNotValidException
from bitcoin_wallet.core.exception.no_more_wallets import NoMoreWalletsLeftException
from bitcoin_wallet.core.exception.user_not_found import UserNotFoundException
from bitcoin_wallet.core.exception.wallet_already_present import (
    WalletAlreadyPresentException,
)
from bitcoin_wallet.core.path.db_path_handler import DatabasePathHandler
from bitcoin_wallet.core.validation.email_validator import EmailValidator


class BaseUserRepository(Protocol):
    def create(self, user: BaseUser) -> int:
        pass

    def read(self, user_id: int) -> BaseUser:
        pass

    def read_all(self) -> list[BaseUser]:
        pass

    def update(self, user: BaseUser) -> None:
        pass

    def delete(self, user_id: int) -> None:
        pass


class BtcUserRepository:
    WALLET_DEFAULT_ID: int = 0

    def __init__(self, db_file: str = "bitcoin_wallet.db") -> None:
        self.filename = DatabasePathHandler.get_db_path(db_file)

    def create(self, user: BaseUser) -> int:
        conn = sqlite3.connect(self.filename)
        cursor: Cursor = conn.cursor()
        find_by_mail_query: str = "SELECT * FROM users WHERE mail = ?"
        cursor.execute(find_by_mail_query, (user.mail,))
        mail_exists = cursor.fetchone()

        if mail_exists:
            raise MailAlreadyPresentException(user.mail)

        if not EmailValidator.check_if_mail_valid(user.mail):
            raise MailNotValidException(user.mail)

        cursor.execute("INSERT INTO users (mail) VALUES (?)", (user.mail,))
        query_result = cursor.execute(find_by_mail_query, (user.mail,)).fetchone()
        conn.commit()
        return int(query_result[0])

    def read(self, user_id: int) -> BaseUser:
        conn = sqlite3.connect(self.filename)
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return BtcUser(*row)
        raise UserNotFoundException(user_id)

    def read_all(self) -> list[BaseUser]:
        conn = sqlite3.connect(self.filename)
        cursor: Cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        users: list[BaseUser] = []
        for row in rows:
            user = BtcUser(*row)
            users.append(user)
        return users

    def update(self, user: BaseUser) -> None:
        pass

    def register_new_wallet(self, user_id: int, new_wallet_id: int) -> None:
        user: BtcUser = cast(BtcUser, self.read(user_id))
        if self.WALLET_DEFAULT_ID not in (
            user.first_wallet_id,
            user.second_wallet_id,
            user.third_wallet_id,
        ):
            raise NoMoreWalletsLeftException(user_id)

        if new_wallet_id in (
            user.first_wallet_id,
            user.second_wallet_id,
            user.third_wallet_id,
        ):
            raise WalletAlreadyPresentException(user_id, new_wallet_id)

        conn = sqlite3.connect(self.filename)
        cursor: Cursor = conn.cursor()
        if user.first_wallet_id == self.WALLET_DEFAULT_ID:
            cursor.execute(
                "UPDATE users SET first_wallet_id = ? WHERE id = ?",
                (new_wallet_id, user_id),
            )
            conn.commit()
            return

        if user.second_wallet_id == self.WALLET_DEFAULT_ID:
            cursor.execute(
                "UPDATE users SET second_wallet_id = ? WHERE id = ?",
                (new_wallet_id, user_id),
            )
            conn.commit()
            return

        if user.third_wallet_id == self.WALLET_DEFAULT_ID:
            cursor.execute(
                "UPDATE users SET third_wallet_id = ? WHERE id = ?",
                (new_wallet_id, user_id),
            )
            conn.commit()
            return

    def delete(self, user_id: int) -> None:
        pass
