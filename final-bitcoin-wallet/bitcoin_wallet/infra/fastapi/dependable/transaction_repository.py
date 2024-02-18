from typing import Annotated

from fastapi import Depends

from bitcoin_wallet.core.repository.transaction_repository import (
    BaseTransactionRepository,
)
from bitcoin_wallet.infra.fastapi.repository.transaction import (
    get_transaction_repository,
)

TransactionRepositoryDependable = Annotated[
    BaseTransactionRepository, Depends(get_transaction_repository)
]
