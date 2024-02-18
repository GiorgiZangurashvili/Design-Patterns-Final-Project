from fastapi import APIRouter, HTTPException

from bitcoin_wallet.core.config.constants import ADMIN_API_KEY, USER_DEFAULT_ID
from bitcoin_wallet.core.entity.user import BtcUser
from bitcoin_wallet.core.exception.mail_already_present import (
    MailAlreadyPresentException,
)
from bitcoin_wallet.core.exception.mail_not_valid import MailNotValidException
from bitcoin_wallet.infra.fastapi.dependable.transaction_repository import (
    TransactionRepositoryDependable,
)
from bitcoin_wallet.infra.fastapi.dependable.user_repository import (
    UserRepositoryDependable,
)
from bitcoin_wallet.infra.fastapi.dependable.wallet_repository import (
    WalletRepositoryDependable,
)
from bitcoin_wallet.infra.fastapi.request.create_user_request import CreateUserRequest
from bitcoin_wallet.infra.fastapi.request.create_wallet_request import (
    CreateWalletRequest,
)

api = APIRouter()


@api.post("/users", status_code=201)
def create_user(
    request: CreateUserRequest, users: UserRepositoryDependable
) -> dict[str, int]:
    try:
        btc_user_id = users.create(BtcUser(USER_DEFAULT_ID, request.mail))
        return {"api_key": btc_user_id}
    except MailAlreadyPresentException:
        raise HTTPException(
            status_code=400, detail="Mail that you have provided is already registered"
        )
    except MailNotValidException as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@api.post("/wallets", status_code=201)
def create_wallet(
    request: CreateWalletRequest, wallets: WalletRepositoryDependable
) -> dict[str, object]:
    if not wallets.authorize_user(request.user_id):
        raise HTTPException(
            status_code=404, detail=f"User with ID {request.user_id} not found."
        )

    wallet_dto = wallets.create_wallet(request.user_id, request.initial_balance)

    return {
        "wallet_id": wallet_dto.wallet_id,
        "balance_in_btc": wallet_dto.balance_in_btc,
        "balance_in_usd": wallet_dto.balance_in_usd,
    }


@api.get("/wallets/{address}", response_model=dict[str, object])
def get_wallet_info(
    user_id: int, address: int, wallets: WalletRepositoryDependable
) -> dict[str, object]:
    if not wallets.authorize_user(user_id):
        raise HTTPException(
            status_code=404, detail=f"User with ID {user_id} not found."
        )

    wallet_info = wallets.retrieve_wallet_info(user_id, address)

    if wallet_info is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "wallet_id": wallet_info.wallet_id,
        "balance_in_btc": wallet_info.balance_in_btc,
        "balance_in_usd": wallet_info.balance_in_usd,
    }


@api.post("/transactions", status_code=201)
def make_transaction(
    from_wallet_id: int,
    to_wallet_id: int,
    amount_transferred: float,
    user_id: int,
    transactions: TransactionRepositoryDependable,
) -> dict[str, int | None]:
    try:
        if not transactions.authorize_transaction(from_wallet_id, user_id):
            raise HTTPException(
                status_code=403,
                detail="User is not authorized to perform this transaction.",
            )

        transaction_id = transactions.make_transaction(
            from_wallet_id, to_wallet_id, amount_transferred
        )
        return {"transaction_id": transaction_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.get("/transactions", response_model=list[dict[str, object]])
def get_transactions(
    user_id: int, transactions: TransactionRepositoryDependable
) -> list[dict[str, object]]:
    try:
        user_transactions = transactions.get_user_transactions(user_id)
        return [
            {
                "transaction_id": transaction.id,
                "from_wallet_id": transaction.from_wallet_id,
                "to_wallet_id": transaction.to_wallet_id,
                "amount_transferred": transaction.amount_transferred,
                "lost_amount": transaction.lost_amount,
            }
            for transaction in user_transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.get("/wallets/{address}/transactions", response_model=list[dict[str, object]])
def get_wallet_transactions(
    address: int, user_id: int, transactions: TransactionRepositoryDependable
) -> list[dict[str, object]]:
    try:
        wallet_belongs_to_user = transactions.authorize_transaction(address, user_id)
        if not wallet_belongs_to_user:
            raise HTTPException(
                status_code=403, detail="Unauthorized access to wallet transactions"
            )

        wallet_transactions = transactions.get_wallet_transactions(address)
        return [
            {
                "transaction_id": transaction.id,
                "from_wallet_id": transaction.from_wallet_id,
                "to_wallet_id": transaction.to_wallet_id,
                "amount_transferred": transaction.amount_transferred,
                "lost_amount": transaction.lost_amount,
            }
            for transaction in wallet_transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.get("/statistics", status_code=200)
def get_transaction_statistics(
    admin_api_key: str, transactions: TransactionRepositoryDependable
) -> dict[str, object]:
    if admin_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized to do this operation")
    all_transactions = transactions.read_all()
    return {
        "Total number of transactions": len(all_transactions),
        "Platform profit": sum(
            transaction.lost_amount for transaction in all_transactions
        ),
    }
