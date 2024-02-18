class WalletNotFoundException(Exception):
    def __init__(self, wallet_id: int) -> None:
        self.wallet_id = wallet_id
        super().__init__(f"Wallet with ID {wallet_id} not found.")
