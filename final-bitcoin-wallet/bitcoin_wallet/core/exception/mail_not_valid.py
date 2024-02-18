class MailNotValidException(Exception):
    def __init__(self, mail: str) -> None:
        self.mail = mail
        super().__init__(f"Mail: {mail} is in invalid format")
