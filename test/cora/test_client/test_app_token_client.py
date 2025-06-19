import pytest
from unittest.mock import MagicMock
from cora.client.app_token_client import AppTokenClient


@pytest.fixture
def setup_client():
    mock_time = MagicMock()
    mock_threading = MagicMock()
    mock_requests = MagicMock()

    login_url = 'https://cora.epc.ub.uu.se/diva/login/rest/apptoken'
    login_id = 'divaAdmin@cora.epc.ub.uu.se'
    app_token = '49ce00fb-68b5-4089-a5f7-1c225d3cf156'
    
    dependencies = {"requests": mock_requests,
                    "time": mock_time,
                    "threading": mock_threading}
    login_spec = {"login_url": login_url,
                  "login_id": login_id,
                  "app_token": app_token}
    client = AppTokenClient(dependencies)
    return {
        "mock_time": mock_time,
        "mock_threading": mock_threading,
        "mock_requests": mock_requests,
        "login_url": login_url,
        "login_id": login_id,
        "app_token": app_token,
        "dependencies": dependencies,
        "login_spec": login_spec,
        "client": client
    }

def test_mocks_are_created(setup_client):
    assert setup_client["mock_time"] is not None
    assert setup_client["mock_threading"] is not None
    assert setup_client["mock_requests"] is not None

def test_dependencies_are_set_correctly(setup_client):
    deps = setup_client["dependencies"]
    assert deps["requests"] is setup_client["mock_requests"]
    assert deps["time"] is setup_client["mock_time"]
    assert deps["threading"] is setup_client["mock_threading"]

def test_login_spec_is_set_correctly(setup_client):
    spec = setup_client["login_spec"]
    assert spec["login_url"] == setup_client["login_url"]
    assert spec["login_id"] == setup_client["login_id"]
    assert spec["app_token"] == setup_client["app_token"]

def test_client_is_initialized(setup_client):
    assert setup_client["client"] is not None
    assert isinstance(setup_client["client"], AppTokenClient)