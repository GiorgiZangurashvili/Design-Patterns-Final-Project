class AuthorisationException(Exception):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"Invalid user key: {user_id}")
