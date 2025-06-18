import pytest
from cora.client.LoginError import LoginError

def test_login_error_message():
    error = LoginError("Login failed")
    assert str(error) == "Login failed"

def test_login_error_with_original_exception():
    original = ValueError("Invalid input")
    error = LoginError("Login failed", original)
    assert str(error) == "Login failed"
    assert error.original_exception is original
    assert str(error.original_exception) == "Invalid input" 