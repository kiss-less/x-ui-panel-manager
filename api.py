import requests, logging, random, string, json
from inbound import Inbound

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class PanelAPI:
    def __init__(self, base_url: str, start_port: int = 46000, prefix: str = None):
        self.base_url: str = f"{base_url}/{prefix}" if prefix else base_url
        self.start_port: int = start_port
        self.headers: dict = {}
        logger.info("PanelAPI object has been initialized")

    def auth(self, username: str, password: str, endoint: str = "/login"):
        url = f"{self.base_url}{endoint}"
        logger.info(f"Authenticating via {url}")
        body = {
            "username": username,
            "password": password
        }

        response = requests.post(url, json=body)

        if response.status_code == 200 and "Set-Cookie" in response.headers:
            self.headers["Cookie"] = response.headers["Set-Cookie"]
            logger.info("Authenticated successfully, cookie set")
        else:
            logger.error(f"Error during auth! Response code: {response.status_code}")
    
    def get_inbounds(self, endpoint: str = "/xui/API/inbounds/") -> dict:
        if not "Cookie" in self.headers:
            logger.error("Authenticate or add a cookie header manually to the PanelAPI.headers dictionary first!")
            return {'success': False}
        else:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Getting inbounds from {url}")
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                logger.info(f"Got 200 from {url}") 
                try:
                    return response.json()
                except Exception as ex:
                    logger.error(f"Exception from get_inbounds: {ex}")
                    return {'success': False}
            else:
                logger.info(f"Got {response.status_code} from {url}")
                return {'success': False}
    
    def create_inbound(self, remark: str, endpoint: str = "/xui/API/inbounds/add", protocol: str = "shadowsocks", method = "aes-256-gcm", password_len: int = 32, enable: bool = True, email: str = "", tg_id: str = "", expiry_time: int = 0) -> dict:
        logger.info(f"Adding a new inbound connection for {remark} with {protocol} protocol")
        if not "Cookie" in self.headers:
            logger.error("Authenticate of add a cookie header manually first!")
            return {'success': False}
        else:
            inbounds = self.get_inbounds()
            if inbounds.get("success") != False:
                if inbounds != {}:
                    logger.info("Getting max port existing to iterate")
                    port = max(inbounds["obj"], key=lambda d: d["port"])["port"] + 1
                    logger.info(f"Max port found. The next port: {port}")
                else:
                    logger.info(f"No existing inbound connections found. Starting a new one from port {self.start_port}")
                    port = self.start_port

                characters = string.ascii_letters + string.digits
                password = ''.join(random.choice(characters) for _ in range(password_len))
                logger.info("Password has been generated")
                url = f"{self.base_url}{endpoint}"
                headers = self.headers | {"Content-Type": "application/x-www-form-urlencoded"}
                if email == "":
                    email = f"{remark}@{remark}.com" # Adding default email to avoid issue with 404 during the updateClient call
                data = {
                    "remark": remark,
                    "enable": enable,
                    "port": port,
                    "protocol": protocol,
                    "settings": f"{{\n  \"clients\": [\n    {{\n      \"email\": \"{email}\",\n      \"enable\": {str(enable).lower()},\n      \"expiryTime\": {expiry_time},\n      \"method\": \"{method}\",\n      \"password\": \"{password}\",\n      \"reset\": 0,\n      \"tgId\": \"{tg_id}\",\n      \"totalGB\": 0\n    }}\n  ],\n  \"method\": \"{method}\",\n  \"network\": \"tcp,udp\",\n  \"password\": \"{password}\"\n}}"
                }
                response = requests.post(url, data=data, headers=headers)
                if response.status_code == 200 and response.json().get('success') == True:
                    logger.info("Inbound has been created")
                    created_inbound = response.json().get("obj")
                    created_client = json.loads(created_inbound.get("settings")).get("clients")[0]
                    inbound = Inbound(created_inbound.get("id"), created_inbound.get("remark"), port, created_inbound.get("protocol"), created_client.get("method"), created_client.get("password"), created_client.get("enable"), created_client.get("email"), created_client.get("tgId"), created_client.get("expiryTime"))
                    return {'success': True, 'inbound': inbound}
                else:
                    logger.error(f"Error during inbound creation! Response code: {response.status_code}")
                    return {'success': False}
            else:
                return {'success': False}

    def update_inbound_expiry_date(self, id: int, new_data: dict, endpoint: str = "/xui/API/inbounds/update") -> dict:
        logger.info(f"Updating inbound with id {id}. New inbound data: {new_data}")
        if not "Cookie" in self.headers:
            logger.error("Authenticate of add a cookie header manually first!")
            return {'success': False}
        else:
            url = f"{self.base_url}{endpoint}/{id}"
            headers = self.headers | {"Content-Type": "application/x-www-form-urlencoded"}
            data = new_data
            response = requests.post(url, data=data, headers=headers)
            logger.info(response.status_code)
            if response.status_code == 200 and response.json().get('success') == True:
                logger.info("Inbound has been updated")
                return {'success': True, 'response': response.json()}
