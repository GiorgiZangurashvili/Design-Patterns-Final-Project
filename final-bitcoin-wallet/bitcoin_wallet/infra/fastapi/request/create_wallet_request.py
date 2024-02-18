from pydantic import BaseModel


class CreateWalletRequest(BaseModel):
    user_id: int
    initial_balance: int
