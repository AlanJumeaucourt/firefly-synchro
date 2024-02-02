import logging
import base64
import requests

logger = logging.getLogger(__name__)


class Ntfy:
    def __init__(
        self, ntfy_url: str, ntfy_topic: str, ntfy_username: str, ntfy_password: str
    ):
        self.url = ntfy_url
        self.topic = ntfy_topic
        self.authHeader = (
            "Basic "
            + base64.b64encode(f"{ntfy_username}:{ntfy_password}".encode()).decode()
        )  # -> Basic dGVzdHVzZXI6ZmFrZXBhc3N3b3Jk

    def send_notification(self, message: str):
        response = requests.post(
            f"{self.url}/{self.topic}",
            data=message,
            headers={"Authorization": self.authHeader},
        )
        
        logger.info(response.text)
        