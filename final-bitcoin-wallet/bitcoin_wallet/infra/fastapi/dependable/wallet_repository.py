from typing import Annotated

from fastapi import Depends

from bitcoin_wallet.core.repository.wallet_repository import BaseWalletRepository
from bitcoin_wallet.infra.fastapi.repository.wallet import get_wallet_repository

WalletRepositoryDependable = Annotated[
    BaseWalletRepository, Depends(get_wallet_repository)
]
