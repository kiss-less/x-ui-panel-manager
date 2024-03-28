from datetime import datetime
import os

class Utils:
    @staticmethod
    def string_to_unix(date_string, format: str = "%d.%m.%Y", milliseconds: bool = True):
        try:
            date_obj = datetime.strptime(date_string, format)
            unix_timestamp = date_obj.timestamp()
            if milliseconds:
                unix_timestamp *= 1000

            return int(unix_timestamp)

        except ValueError:
            return 0

    @staticmethod
    def unix_to_string(unix_timestamp: int, format: str = "%d.%m.%y", milliseconds: bool = True) -> str:
        try:
            if milliseconds:
                unix_timestamp /= 1000
            date_obj = datetime.fromtimestamp(unix_timestamp)
            return date_obj.strftime(format)
        except ValueError:
            return ""

    @staticmethod
    def cookie_file_exists(file_path: str = "./cookie.json") -> bool:
        if os.path.exists(file_path):
            return True
        else:
            return False

    @staticmethod
    def cookie_file_is_about_to_expire(file_path: str = "./cookie.json", expiry_days: int = 30) -> bool:
        modified_timestamp = os.path.getmtime(file_path)
        current_timestamp = datetime.now().timestamp()

        days_difference = (current_timestamp - modified_timestamp) / (24 * 60 * 60)

        if days_difference < (expiry_days -1):
            return False
        else:
            return True
