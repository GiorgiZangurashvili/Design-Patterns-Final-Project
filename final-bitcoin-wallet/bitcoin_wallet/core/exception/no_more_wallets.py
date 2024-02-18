class NoMoreWalletsLeftException(Exception):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} can not create more wallets")
