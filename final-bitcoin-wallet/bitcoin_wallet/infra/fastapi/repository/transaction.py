from fastapi.requests import Request

from bitcoin_wallet.core.repository.transaction_repository import (
    BaseTransactionRepository,
)


def get_transaction_repository(request: Request) -> BaseTransactionRepository:
    return request.app.state.transactions  # type: ignore
