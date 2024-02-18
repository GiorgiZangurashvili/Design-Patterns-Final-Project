from dataclasses import dataclass


@dataclass
class BaseTransaction:
    id: int
    from_wallet_id: int
    to_wallet_id: int
    amount_transferred: float

    def __init__(self) -> None:
        pass


@dataclass
class BtcTransaction(BaseTransaction):
    id: int
    from_wallet_id: int
    to_wallet_id: int
    amount_transferred: float
    lost_amount: float

    def __hash__(self) -> int:
        return hash(self.id)
