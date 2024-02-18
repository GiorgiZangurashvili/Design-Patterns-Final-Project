class SameTransferWalletsException(Exception):
    def __init__(self, from_wallet_id: int, to_wallet_id: int) -> None:
        self.from_wallet_id = from_wallet_id
        self.to_wallet_id = to_wallet_id
        super().__init__(
            f"Cannot transfer from wallet {from_wallet_id} to "
            f"wallet {to_wallet_id}, they are the same"
        )
