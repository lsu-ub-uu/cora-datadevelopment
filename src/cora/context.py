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
from unittest.mock import MagicMock
from cora.get_deployment_info import get_deployment_info

main_script = os.path.basename(sys.argv[0])


class Context(Protocol):
    def get_base_url(self) -> str: ...
    def get_auth_token(self) -> str: ...
    def get_logger(self) -> Logger: ...
    def log(
        self, message: str, level: Literal["info", "error", "warning"] = "info"
    ) -> None: ...
    def get_log_file_path(self) -> str: ...
    def get_workers(self) -> int: ...
    def get_system(self) -> str: ...


class CoraContext(Context):
    def __init__(
        self, system: str, login_id: str, app_token: str | None, workers: int = 16
    ):
        self.system = system
        cora_url = os.environ.get("CORA_URL")
        if cora_url:
            cora_url = cora_url.rstrip("/")
            self._base_url = f"{cora_url}/rest/record/"
            login_url = f"{cora_url}/login/rest/apptoken"
        else:
            self._base_url = constants.BASE_URL[self.system]
            login_url = constants.LOGIN_URLS[self.system]
        self._logger = RunRotatingLogger("data", f"logs/{main_script}.log").get()
        self.app_token_client = AppTokenClient(
            dependencies={
                "requests": requests,
                "time": time,
                "threading": threading,
            }
        )
        if app_token is None:
            app_token = _get_app_token_from_example_user(system, login_id)

        self.app_token_client.login(
            {
                "login_url": login_url,
                "login_id": login_id,
                "app_token": app_token,
            }
        )
        self._workers = workers

    def get_system(self) -> str:
        """
        Get the system name for the Cora API.

        :return: The system name as a string.
        """
        return self.system

    def get_base_url(self) -> str:
        """
        Get the base URL for the Cora API based on the system configuration.

        :return: The base URL as a string.
        """
        return self._base_url

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

    def get_log_file_path(self) -> str:
        """
        Get the file path of the log file.

        :return: The log file path as a string.
        """
        return self._logger.handlers[0].baseFilename  # type: ignore[attr-defined]

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

    def get_workers(self) -> int:
        """
        Get the number of worker threads to use for parallel processing.

        :return: The number of worker threads.
        """
        return self._workers

    def close(self):
        return


class MockContext(Context):
    def __init__(
        self,
        base_url: str = "https://pre.diva-portal.org/rest/record/",
        auth_token: str = "test-token",
        workers: int = 16,
    ):
        self._base_url = base_url
        self._auth_token = auth_token
        self._workers = workers
        self.log = MagicMock()

    def log(
        self, message: str, level: Literal["info", "error", "warning"] = "info"
    ) -> None:
        pass

    def get_base_url(self):
        return self._base_url

    def get_auth_token(self):
        return self._auth_token

    def get_logger(self):
        return MagicMock()

    def get_log_file_path(self) -> str:
        return "mock_log_file.log"

    def get_workers(self) -> int:
        return self._workers

    def get_system(self) -> str:
        return "mock_system"


def _get_app_token_from_example_user(system: str, login_id: str) -> str:
    deployment_info = get_deployment_info(system)
    example_users = deployment_info.get("exampleUsers", [])
    for user in example_users:
        if user.get("type") == "appTokenLogin" and user.get("loginId") == login_id:
            return user["appToken"]
    raise ValueError(
        f"No example user found with login ID '{login_id}' for app token login."
    )
