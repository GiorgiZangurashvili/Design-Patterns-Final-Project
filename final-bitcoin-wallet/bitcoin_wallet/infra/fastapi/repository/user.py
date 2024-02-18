from fastapi.requests import Request

from bitcoin_wallet.core.repository.user_repository import BaseUserRepository


def get_user_repository(request: Request) -> BaseUserRepository:
    return request.app.state.users  # type: ignore
