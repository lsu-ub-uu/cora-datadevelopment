from cora.client.app_token_client import AppTokenClient
from cora import constants
import requests
import time
import threading
from typing import Protocol
from cora.get_deployment_info import get_deployment_info


class Context(Protocol):
    def get_base_url(self) -> str: ...
    def get_workers(self) -> int: ...
    def get_auth_token(self) -> str: ...
    def get_system(self) -> str: ...


class CoraContext(Context):
    def __init__(
        self,
        system: str,
        login_id: str,
        app_token: str | None,
        workers: int = 16,
        cora_url: str | None = None,
    ):
        self.system = system
        if cora_url:
            cora_url = cora_url.rstrip("/")
            self._base_url = f"{cora_url}/rest/record/"
            login_url = f"{cora_url}/login/rest/apptoken"
        else:
            self._base_url = constants.BASE_URL[self.system]
            login_url = constants.LOGIN_URLS[self.system]
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

    def get_base_url(self):
        return self._base_url

    def get_auth_token(self):
        return self._auth_token

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
