import logging, time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
    
def convert_unix(unix_timestamp: int, format: str = "%Y-%m-%d %H:%M:%S GMT"):
    if unix_timestamp > 0:
        struct_time = time.gmtime(unix_timestamp / 1000)
        return time.strftime(format, struct_time)
    else:
        return "0"

class Inbound:
    def __init__(self, id: int, remark: str, port: int, protocol: str, method: str, password: str, enable: bool, email: str, tg_id: str, expiry_time: int):
        self.id: int = id
        self.remark: str = remark
        self.port: int = port
        self.protocol: str = protocol
        self.method: str = method
        self.password: str = password
        self.enable: bool = enable
        self.email: str = email
        self.tg_id: str = tg_id
        self.expiry_time: int = expiry_time
        logger.info("Inbound object has been initialized")


    def display_credentials(self, display_password: bool = False, unix_timestamp: bool = False, essential_only: bool = False):
        if display_password:
            password = self.password
        else:
            password = "<Sensitive data>"
        
        if unix_timestamp:
            expiry = self.expiry_time
        else:
            expiry = convert_unix(self.expiry_time)
        
        if essential_only:
            return f"Remark: {self.remark}, Port: {self.port}, Password: {password}"
        else:
            return f"Remark: {self.remark}, Email: {self.email}, Port: {self.port}, Encryption method: {self.method}, Password: {password}, Enabled: {self.enable}, Expity Time: {expiry}"
