from typing import Annotated

from fastapi import Depends

from bitcoin_wallet.core.repository.user_repository import BaseUserRepository
from bitcoin_wallet.infra.fastapi.repository.user import get_user_repository

UserRepositoryDependable = Annotated[BaseUserRepository, Depends(get_user_repository)]
