from dataclasses import dataclass, field


@dataclass
class BaseUser:
    id: int
    mail: str

    def __init__(self) -> None:
        pass


@dataclass
class BtcUser(BaseUser):
    id: int
    mail: str
    first_wallet_id: int = field(default=0)
    second_wallet_id: int = field(default=0)
    third_wallet_id: int = field(default=0)

    def __hash__(self) -> int:
        return hash(self.id)
