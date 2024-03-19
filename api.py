import requests, logging, random, string

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class PanelAPI:
    def __init__(self, base_url: str, start_port: int = 46000, prefix: str = None):
        if prefix:
            self.base_url: str = f"{base_url}/{prefix}"
        else:
            self.base_url: str = base_url
        self.start_port: int = start_port
        logger.info("PanelAPI object has been initialized")

    def auth(self, username: str, password: str):
        url = f"{self.base_url}/login"
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
    
    def get_inbounds(self, endpoint: str = "/xui/API/inbounds/"):
        if not "Cookie" in self.headers:
            logger.error("Authenticate or add a cookie header manually first!")
            return {'success': False}
        else:
            url = f"{self.base_url}{endpoint}"
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
    
    def create_inbound(self, remark: str, endpoint: str = "/xui/API/inbounds/add", protocol: str = "shadowsocks", password_len: int = 32, enable: bool = True, expiry_time: int = 0):
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
                data = {
                    "remark": remark,
                    "enable": enable,
                    "port": port,
                    "protocol": protocol,
                    "settings": "{{\n  \"method\": \"aes-256-gcm\",\n  \"password\": \"{}\",\n  \"network\": \"tcp,udp\",\n  \"clients\": [\n    {{\n      \"method\": \"aes-256-gcm\",\n      \"password\": \"{}\",\n      \"email\": \"\",\n      \"totalGB\": 0,\n      \"expiryTime\": {},\n      \"enable\": true,\n      \"tgId\": \"\",\n      \"reset\": 0\n    }}\n  ]\n}}".format(password, password, expiry_time)
                }
                response = requests.post(url, data=data, headers=headers)
                if response.status_code == 200 and response.json().get('success') == True:
                    logger.info("Inbound has been created")
                    return response.json()
                else:
                    logger.error(f"Error during inbound creation! Response code: {response.status_code}")
                    return {'success': False}
            else:
                return {'success': False}
