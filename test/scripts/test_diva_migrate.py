import sys
from unittest.mock import Mock

import pytest

from scripts import diva_migrate


def test_main_uses_configured_app_token(monkeypatch):
    monkeypatch.setenv("CORA_APP_TOKEN", "test-token")
    monkeypatch.setenv("CORA_LOGIN_ID", "test-login")
    monkeypatch.setenv("CORA_SYSTEM", "test-system")
    monkeypatch.setenv("CORA_WORKERS", "3")
    monkeypatch.setattr(
        sys,
        "argv",
        ["diva-migrate", "--domain", "norden", "--cora-url", "https://example.org"],
    )
    monkeypatch.setattr(diva_migrate, "configure_logging", lambda: None)
    load_environment = Mock()
    monkeypatch.setattr(diva_migrate, "load_environment", load_environment)

    class ContextCreated(Exception):
        pass

    def capture_context(system, login_id, app_token, **kwargs):
        assert system == "test-system"
        assert login_id == "test-login"
        assert app_token is None
        assert kwargs["workers"] == 3
        raise ContextCreated

    monkeypatch.setattr(diva_migrate, "CoraContext", capture_context)

    with pytest.raises(ContextCreated):
        diva_migrate.main()

    load_environment.assert_called_once_with()
