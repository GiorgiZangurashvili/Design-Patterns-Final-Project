import re


class EmailValidator:
    @staticmethod
    def check_if_mail_valid(email: str) -> bool:
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        match = re.fullmatch(regex, email)
        if match:
            return True
        else:
            return False
