from cora.context import CoraContext
from unittest.mock import patch
from cora import constants


@patch("cora.context.AppTokenClient")
def test_context_logs_in_on_creation(AppTokenClientMock):
    context = CoraContext(
        system="minikube", login_id="someLoginId", app_token="test-token"
    )
    AppTokenClientMock.assert_called_once()
    instance = AppTokenClientMock.return_value
    instance.get_auth_token = lambda: "mocked-token"
    instance.login.assert_called_once_with(
        {
            "login_url": constants.LOGIN_URLS["minikube"],
            "login_id": "someLoginId",
            "app_token": "test-token",
        }
    )
    assert context.get_auth_token() == "mocked-token"


@patch("cora.context.AppTokenClient")
@patch("cora.context.get_deployment_info")
def test_context_logs_in_with_example_user_when_no_app_token(
    get_deployment_info_mock, AppTokenClientMock
):
    get_deployment_info_mock.return_value = {
        "exampleUsers": [
            {
                "name": "Example user",
                "type": "appTokenLogin",
                "loginId": "exampleLoginId",
                "appToken": "exampleAppToken",
            },
            {
                "name": "Another user",
                "type": "appTokenLogin",
                "loginId": "anotherLoginId",
                "appToken": "anotherAppToken",
            },
        ]
    }
    context = CoraContext(system="dev", login_id="exampleLoginId", app_token=None)

    get_deployment_info_mock.assert_called_once_with("dev")

    AppTokenClientMock.assert_called_once()
    instance = AppTokenClientMock.return_value
    instance.get_auth_token = lambda: "mocked-token"
    instance.login.assert_called_once_with(
        {
            "login_url": constants.LOGIN_URLS["dev"],
            "login_id": "exampleLoginId",
            "app_token": "exampleAppToken",
        }
    )
