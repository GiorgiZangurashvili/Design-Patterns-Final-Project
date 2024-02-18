import os


class DatabasePathHandler:
    @staticmethod
    def get_db_path(db_filename: str) -> str:
        db_filename = f"../../{db_filename}"
        main_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(main_dir, db_filename)
