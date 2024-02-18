class MailAlreadyPresentException(Exception):
    def __init__(self, mail: str) -> None:
        self.mail = mail
        super().__init__(f"User with mail {mail} already exists")
