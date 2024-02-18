from fastapi import FastAPI

from bitcoin_wallet.core.repository.transaction_repository import (
    BtcTransactionRepository,
)
from bitcoin_wallet.core.repository.user_repository import BtcUserRepository
from bitcoin_wallet.core.repository.wallet_repository import BtcWalletRepository
from bitcoin_wallet.infra.fastapi.api.api import api

app = FastAPI()
app.include_router(api)

app.state.users = BtcUserRepository()
app.state.wallets = BtcWalletRepository()
app.state.transactions = BtcTransactionRepository()
