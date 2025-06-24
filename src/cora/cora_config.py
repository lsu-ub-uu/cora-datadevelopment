from cora.client.app_token_client import AppTokenClient
from cora import constants
import requests
import time
import threading
from typing import Protocol


class CoraConfig:
    def __init__(self, system: str, login_id: str, app_token: str):
        self.system = system
        self.app_token_client = AppTokenClient(
            dependencies={
                "requests": requests,
                "time": time,
                "threading": threading,
            }
        )
        self.app_token_client.login(
            {
                "login_url": constants.LOGIN_URLS[self.system],
                "login_id": login_id,
                "app_token": app_token,
            }
        )

    def get_base_url(self) -> str:
        """
        Get the base URL for the Cora API based on the system configuration.

        :return: The base URL as a string.
        """
        return constants.BASE_URL[self.system]

    def get_auth_token(self) -> str:
        """
        Get the authentication token for the Cora API.

        :return: The authentication token as a string.
        """
        return str(self.app_token_client.get_auth_token())

    def close(self):
        return


class CoraConfigProtocol(Protocol):
    def get_base_url(self) -> str: ...
    def get_auth_token(self) -> str: ...
