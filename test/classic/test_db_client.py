from unittest.mock import patch

import pytest

from classic.db_client import execute_sql


def test_execute_sql_uses_environment_connection_settings(monkeypatch):
    monkeypatch.setenv("DB_HOST", "db.example")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "test-db")
    monkeypatch.setenv("DB_USER", "test-user")
    monkeypatch.setenv("DB_PASSWORD", "test-password")

    with patch("classic.db_client.psycopg2.connect") as connect:
        cursor = (
            connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
        )
        cursor.fetchall.return_value = []
        cursor.description = [("id",)]

        execute_sql(
            "SELECT 1",
            db_host=None,
            db_port=None,
            db_name=None,
            db_user=None,
            db_password=None,
        )

    connect.assert_called_once_with(
        dbname="test-db",
        user="test-user",
        password="test-password",
        host="db.example",
        port=5433,
    )


def test_execute_sql_requires_credentials_at_use_time(monkeypatch):
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)

    with pytest.raises(ValueError, match="DB_USER"):
        execute_sql(
            "SELECT 1",
            db_host=None,
            db_port=None,
            db_name=None,
            db_user=None,
            db_password=None,
        )
