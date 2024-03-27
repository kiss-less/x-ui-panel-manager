import gspread
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class GSpreadsheet:
    def __init__(self, credentials_file: str, spread_key: str, usernames_starting_column: int = 5, time_delta_start_date: str = "19.01.2023", strip_first_symbol_from_username: bool = True, worksheet_name: str = "Donations"):
        result = {}
        gc = gspread.service_account(credentials_file)
        logger.debug(f"Connected to Google Spreadsheet using {credentials_file}")
        sh = gc.open_by_key(spread_key).worksheet(worksheet_name)
        logger.debug(f"Opened to worksheet {worksheet_name}")
        usernames = dict(enumerate(sh.col_values(1)))
        for _ in range(usernames_starting_column):
            usernames.pop(next(iter(usernames)))
        logger.debug(f"Received usernames: {usernames}")
        
        for col_index in usernames:
            row_values = sh.row_values(col_index)
            logger.debug(f"Received row values for column {col_index}: {row_values}")
            if strip_first_symbol_from_username:
                username = row_values[0][1:]
            else:
                username = row_values[0]
            years_to_add = (len(row_values) - 1) // 12
            months_remaining = (len(row_values) - 1) % 12
            time_delta = datetime.strptime(time_delta_start_date, "%d.%m.%Y") + timedelta(days=365*years_to_add) + timedelta(days=30*months_remaining)
            logger.debug(f"Calculated delta from {time_delta_start_date}, adding {years_to_add} years, {months_remaining} months")
            expiry_date = time_delta.strftime("%m.%Y")
            result[username] = f"{time_delta_start_date[0:3]}{expiry_date}"
        
        logger.debug(f"result: {result}")
        self.user_expiry_dates = result
