import sqlite3
from typing import Protocol

from fastapi import HTTPException

from bitcoin_wallet.core.currencyconverter.convert_api import BitfinexConverter
from bitcoin_wallet.core.dto.wallet_dto import WalletDTO
from bitcoin_wallet.core.exception.no_more_wallets import NoMoreWalletsLeftException
from bitcoin_wallet.core.exception.user_not_found import UserNotFoundException
from bitcoin_wallet.core.path.db_path_handler import DatabasePathHandler
from bitcoin_wallet.core.repository.user_repository import BtcUserRepository


class BaseWalletRepository(Protocol):
    def create_wallet(self, user_id: int, initial_balance: int) -> WalletDTO:
        pass

    def retrieve_wallet_info(self, user_id: int, wallet_id: int) -> WalletDTO | None:
        pass

    def authorize_user(self, user_id: int) -> bool:
        pass


class BtcWalletRepository:
    def __init__(self, db_file: str = "bitcoin_wallet.db") -> None:
        self.db_name = DatabasePathHandler.get_db_path(db_file)
        self.user_repository = BtcUserRepository(db_file=db_file)
        self.converter = BitfinexConverter()

    def setup(self) -> None:
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            cur.close()

    def authorize_user(self, user_id: int) -> bool:

        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            try:
                user = cur.execute(
                    f"SELECT * FROM users WHERE id = {user_id}"
                ).fetchone()
                if user is None:
                    return False
            except sqlite3.Error:
                raise UserNotFoundException(user_id)

            cur.close()

            return True

    def create_wallet(self, user_id: int, initial_balance: int) -> WalletDTO:

        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            try:
                user = cur.execute(
                    f"SELECT * FROM users WHERE id = {user_id}"
                ).fetchone()

                wallet = ""
                if user[2] == 0:
                    wallet = "first_wallet_id"
                elif user[3] == 0:
                    wallet = "second_wallet_id"
                elif user[4] == 0:
                    wallet = "third_wallet_id"
                else:
                    raise NoMoreWalletsLeftException(user_id)

                cur.execute(
                    f"INSERT INTO wallets (user_id, balance) VALUES "
                    f"({user_id}, {initial_balance})"
                )

                wallet_id = cur.execute("SELECT last_insert_rowid()").fetchone()[0]

                cur.execute(
                    f"UPDATE users SET {wallet} = {wallet_id} WHERE id = {user_id}"
                )

                res = cur.execute(f"SELECT * FROM wallets WHERE id = {wallet_id}")

                wallet = res.fetchone()
                balance: float = float(wallet[2])

                balance_in_usd = self.converter.convert_btc_to_usd() * balance
            except sqlite3.Error:
                raise UserNotFoundException(user_id)

            cur.close()

            return WalletDTO(
                wallet_id=wallet_id,
                balance_in_btc=balance,
                balance_in_usd=balance_in_usd,
            )

    def retrieve_wallet_info(self, user_id: int, wallet_id: int) -> WalletDTO | None:
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()
            try:
                user = cur.execute(
                    f"SELECT * FROM users WHERE id = {user_id}"
                ).fetchone()
                if user[2] == wallet_id or user[3] == wallet_id or user[4] == wallet_id:
                    res = cur.execute(f"SELECT * FROM wallets WHERE id = {wallet_id}")
                    wallet = res.fetchone()
                    if wallet is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Wallet with ID {wallet_id} not found.",
                        )

                    balance = wallet[2]
                    balance_in_usd = self.converter.convert_btc_to_usd() * balance
                else:
                    raise HTTPException(
                        status_code=405,
                        detail=f"User does not have access "
                        f"to this wallet with id {wallet_id}.",
                    )
            except sqlite3.Error:
                return None

            cur.close()

            return WalletDTO(
                wallet_id=wallet_id,
                balance_in_btc=balance,
                balance_in_usd=balance_in_usd,
            )
