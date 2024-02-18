from typing import Protocol

import requests


class ConvertBitcoinToUsd(Protocol):
    def convert_btc_to_usd(self) -> float:
        pass


class BitfinexConverter:
    _URL = "https://api.bitfinex.com/v2/ticker/tBTCUSD"

    def convert_btc_to_usd(self) -> float:
        ans: float = requests.get(self._URL).json()[0]
        return ans
