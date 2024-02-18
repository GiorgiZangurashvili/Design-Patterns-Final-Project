from fastapi.requests import Request

from bitcoin_wallet.core.repository.wallet_repository import BaseWalletRepository


def get_wallet_repository(request: Request) -> BaseWalletRepository:
    return request.app.state.wallets  # type: ignore
