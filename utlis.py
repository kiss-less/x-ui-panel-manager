from datetime import datetime

class Utils:
    @staticmethod
    def string_to_unix(date_string, format: str = "%d.%m.%y", milliseconds: bool = True):
        try:
            date_obj = datetime.strptime(date_string, format)
            unix_timestamp = date_obj.timestamp()
            if milliseconds:
                unix_timestamp *= 1000

            return int(unix_timestamp)

        except ValueError:
            return 0
