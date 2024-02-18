from dataclasses import dataclass


@dataclass
class WalletDTO:
    wallet_id: int
    balance_in_btc: float
    balance_in_usd: float
