from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    mail: str
