from dataclasses import dataclass


@dataclass
class BaseWallet:
    id: int

    def __init__(self) -> None:
        pass


@dataclass
class BtcWallet(BaseWallet):
    id: int
    user_id: int
    balance: float

    def __hash__(self) -> int:
        return hash(self.id)
