class WalletAlreadyPresentException(Exception):
    def __init__(self, user_id: int, wallet_id: int) -> None:
        self.user_id = user_id
        self.wallet_id = wallet_id
        super().__init__(
            f"User with ID {user_id} already has wallet with ID {wallet_id}"
        )
