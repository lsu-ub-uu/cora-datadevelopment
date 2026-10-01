from cora.context import CoraContext
from unittest.mock import patch
from cora import cora_urls


@patch("cora.context.AppTokenClient")
@patch("cora.context.get_deployment_info")
def test_context_uses_environment_token_before_example_user(
    get_deployment_info_mock, AppTokenClientMock, monkeypatch
):
    monkeypatch.setenv("CORA_APP_TOKEN", "env-token")

    CoraContext(system="dev", login_id="test-login", app_token=None)

    get_deployment_info_mock.assert_not_called()
    assert (
        AppTokenClientMock.return_value.login.call_args.args[0]["app_token"]
        == "env-token"
    )


@patch("cora.context.AppTokenClient")
def test_context_explicit_token_overrides_environment(AppTokenClientMock, monkeypatch):
    monkeypatch.setenv("CORA_APP_TOKEN", "env-token")

    CoraContext(system="dev", login_id="test-login", app_token="cli-token")

    assert (
        AppTokenClientMock.return_value.login.call_args.args[0]["app_token"]
        == "cli-token"
    )


@patch("cora.context.AppTokenClient")
def test_context_resolves_missing_cora_settings_from_environment(
    AppTokenClientMock, monkeypatch
):
    monkeypatch.setenv("CORA_SYSTEM", "dev")
    monkeypatch.setenv("CORA_LOGIN_ID", "env-login")
    monkeypatch.setenv("CORA_URL", "https://cora.example/")
    monkeypatch.setenv("CORA_WORKERS", "3")

    context = CoraContext(None, None, "test-token", workers=None, cora_url=None)

    assert context.get_system() == "dev"
    assert context.get_workers() == 3
    assert context.get_base_url() == "https://cora.example/rest/record/"
    AppTokenClientMock.return_value.login.assert_called_once_with(
        {
            "login_url": "https://cora.example/login/rest/apptoken",
            "login_id": "env-login",
            "app_token": "test-token",
        }
    )


@patch("cora.context.AppTokenClient")
def test_explicit_cora_settings_override_environment(AppTokenClientMock, monkeypatch):
    monkeypatch.setenv("CORA_SYSTEM", "dev")
    monkeypatch.setenv("CORA_LOGIN_ID", "env-login")
    monkeypatch.setenv("CORA_URL", "https://env.example")
    monkeypatch.setenv("CORA_WORKERS", "3")

    context = CoraContext(
        "minikube", "cli-login", "test-token", 2, "https://cli.example"
    )

    assert context.get_system() == "minikube"
    assert context.get_workers() == 2
    assert context.get_base_url() == "https://cli.example/rest/record/"
    assert (
        AppTokenClientMock.return_value.login.call_args.args[0]["login_id"]
        == "cli-login"
    )


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
            "login_url": cora_urls.LOGIN_URLS["minikube"],
            "login_id": "someLoginId",
            "app_token": "test-token",
        }
    )
    assert context.get_auth_token() == "mocked-token"


@patch("cora.context.AppTokenClient")
def test_context_builds_urls_from_cora_url_instead_of_system(
    AppTokenClientMock,
):
    context = CoraContext(
        system="not-a-configured-system",
        login_id="someLoginId",
        app_token="test-token",
        cora_url="https://next.diva-portal.org/",
    )

    AppTokenClientMock.return_value.login.assert_called_once_with(
        {
            "login_url": "https://next.diva-portal.org/login/rest/apptoken",
            "login_id": "someLoginId",
            "app_token": "test-token",
        }
    )
    assert context.get_base_url() == "https://next.diva-portal.org/rest/record/"


@patch("cora.context.AppTokenClient")
@patch("cora.context.get_deployment_info")
def test_context_logs_in_with_example_user_when_no_app_token(
    get_deployment_info_mock, AppTokenClientMock, monkeypatch
):
    monkeypatch.delenv("CORA_APP_TOKEN", raising=False)
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
            "login_url": cora_urls.LOGIN_URLS["dev"],
            "login_id": "exampleLoginId",
            "app_token": "exampleAppToken",
        }
    )
