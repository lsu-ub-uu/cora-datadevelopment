from cora.client.app_token_client import AppTokenClient
from cora import constants
import requests
import time
import threading
from typing import Protocol, Literal
from logging import Logger
from common.run_rotating_logger import RunRotatingLogger
import sys
import os

main_script = os.path.basename(sys.argv[0])


class Context(Protocol):
    def get_base_url(self) -> str: ...
    def get_auth_token(self) -> str: ...
    def get_logger(self) -> Logger: ...
    def log(
        self, message: str, level: Literal["info", "error", "warning"] = "info"
    ) -> None: ...


class CoraContext(Context):
    def __init__(self, system: str, login_id: str, app_token: str):
        self.system = system
        self._logger = RunRotatingLogger("data", f"logs/{main_script}.log").get()
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

    def get_logger(self) -> Logger:
        """
        Get the logger instance for logging messages.

        :return: The logger instance.
        """
        return self._logger

    def log(self, message: str, level: Literal["info", "error", "warning"] = "info"):
        """
        Log a message with the specified logging level.

        :param message: The message to log.
        :param level: The logging level (default is "info").
        """
        if level == "info":
            self._logger.info(message)
        elif level == "error":
            self._logger.error(message)
        elif level == "warning":
            self._logger.warning(message)
        else:
            self._logger.debug(message)

    def close(self):
        return


class MockContext(Context):
    def __init__(self, base_url: str, auth_token: str):
        self._base_url = base_url
        self._auth_token = auth_token

    def get_base_url(self):
        return self._base_url

    def get_auth_token(self):
        return self._auth_token

    def get_logger(self):
        return Logger("MockLogger")

    def log(self, message: str, level: Literal["info", "error", "warning"] = "info"):
        print(f"[{level.upper()}] {message}")
