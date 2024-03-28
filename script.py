from user_expiry_dates import GSpreadsheet
from api import PanelAPI
from utils import Utils
import os, json, time


PANEL_USERNAME = os.getenv("PANEL_USER")
PANEL_PASSWORD = os.getenv("PANEL_PWD")
PANEL_BASE_URL = os.getenv("PANEL_BASE_URL")
GSHEET_ID = os.getenv("GSHEET_ID")
GSHEET_CRED = "./cred.json"
COOKIE_FILE = "./cookie.json"
COOKIE_EXPIRY_DAYS = 30
EXECUTION_CYCLE = 21600 # Execute every X seconds. 6 hours by default

while True:
    api = PanelAPI(base_url = PANEL_BASE_URL, prefix = "iux")

    if Utils.cookie_file_exists(COOKIE_FILE) and not Utils.cookie_file_is_about_to_expire(COOKIE_FILE, COOKIE_EXPIRY_DAYS):
        with open(COOKIE_FILE, "r") as cookie_file:
            api.headers = json.load(cookie_file)
    else:
        api.auth(PANEL_USERNAME, PANEL_PASSWORD)
        with open(COOKIE_FILE, "w") as cookie_file:
            json.dump(api.headers, cookie_file, indent=2)

    inbounds = api.get_inbounds().get("obj")
    sheet = GSpreadsheet(GSHEET_CRED, GSHEET_ID)
    user_expiry_dates = sheet.user_expiry_dates

    for user, expiry_date in user_expiry_dates.items():
        for inbound in inbounds:
            if inbound.get("remark") == user:
                current_time = inbound["expiryTime"]
                new_time = Utils.string_to_unix(expiry_date)
                if current_time != new_time:
                    inbound["settings"] = inbound["settings"].replace(str(current_time), str(new_time))
                    new_data = {
                        "remark": inbound["remark"],
                        "expiryTime": new_time,
                        "enable": inbound["enable"],
                        "port": inbound["port"],
                        "protocol": inbound["protocol"],
                        "settings": inbound["settings"]
                    }
                    api.update_inbound_expiry_date(inbound.get("id"), new_data)
    print(f"Sleeping for {EXECUTION_CYCLE / 3600} hours")
    time.sleep(EXECUTION_CYCLE)
