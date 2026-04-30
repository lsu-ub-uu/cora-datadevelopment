from xml.etree import ElementTree as ET
from unittest.mock import MagicMock, patch, call
from scripts.outputs_migrate import main, _print_summary
from fedora_to_cora.output_migrate import OutputMigrationResult


def test_main_migrates_publications(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["outputs_migrate", "--pids", "pid1,pid2", "--system", "pre"],
    )

    mock_context = MagicMock()
    cora_context_mock = MagicMock(return_value=mock_context)
    monkeypatch.setattr("scripts.outputs_migrate.CoraContext", cora_context_mock)

    mock_record_1 = ET.Element("record")
    mock_record_2 = ET.Element("record")

    def fake_get_classic_publications(pids, workers, on_success, on_error):
        on_success("pid1", mock_record_1)
        on_success("pid2", mock_record_2)

    monkeypatch.setattr(
        "scripts.outputs_migrate.get_classic_publications",
        fake_get_classic_publications,
    )

    output_migrate_mock = MagicMock(
        side_effect=[
            OutputMigrationResult("pid1", status="SUCCESS"),
            OutputMigrationResult("pid2", status="SUCCESS"),
        ]
    )
    monkeypatch.setattr("scripts.outputs_migrate.output_migrate", output_migrate_mock)

    ssh_tunnel_mock = MagicMock()
    ssh_tunnel_mock.return_value.__enter__ = MagicMock()
    ssh_tunnel_mock.return_value.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("scripts.outputs_migrate.SSHTunnel", ssh_tunnel_mock)

    main()

    assert output_migrate_mock.call_count == 2
    output_migrate_mock.assert_any_call(
        mock_record_1, mock_context, apply=False, with_binaries=False
    )
    output_migrate_mock.assert_any_call(
        mock_record_2, mock_context, apply=False, with_binaries=False
    )


def test_main_with_apply_and_binaries(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "outputs_migrate",
            "--pids",
            "pid1",
            "--system",
            "pre",
            "--apply",
            "--binaries",
        ],
    )

    mock_context = MagicMock()
    monkeypatch.setattr(
        "scripts.outputs_migrate.CoraContext", MagicMock(return_value=mock_context)
    )

    mock_record = ET.Element("record")

    def fake_get(pids, workers, on_success, on_error):
        on_success("pid1", mock_record)

    monkeypatch.setattr("scripts.outputs_migrate.get_classic_publications", fake_get)

    output_migrate_mock = MagicMock(
        return_value=OutputMigrationResult("pid1", status="SUCCESS")
    )
    monkeypatch.setattr("scripts.outputs_migrate.output_migrate", output_migrate_mock)

    ssh_tunnel_mock = MagicMock()
    ssh_tunnel_mock.return_value.__enter__ = MagicMock()
    ssh_tunnel_mock.return_value.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("scripts.outputs_migrate.SSHTunnel", ssh_tunnel_mock)

    main()

    output_migrate_mock.assert_called_once_with(
        mock_record, mock_context, apply=True, with_binaries=True
    )


def test_main_handles_fetch_error(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["outputs_migrate", "--pids", "pid1", "--system", "pre"],
    )

    mock_context = MagicMock()
    monkeypatch.setattr(
        "scripts.outputs_migrate.CoraContext", MagicMock(return_value=mock_context)
    )

    def fake_get(pids, workers, on_success, on_error):
        on_error("Error fetching record pid1: 404")

    monkeypatch.setattr("scripts.outputs_migrate.get_classic_publications", fake_get)

    output_migrate_mock = MagicMock()
    monkeypatch.setattr("scripts.outputs_migrate.output_migrate", output_migrate_mock)

    ssh_tunnel_mock = MagicMock()
    ssh_tunnel_mock.return_value.__enter__ = MagicMock()
    ssh_tunnel_mock.return_value.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("scripts.outputs_migrate.SSHTunnel", ssh_tunnel_mock)

    main()

    output_migrate_mock.assert_not_called()
    mock_context.log.assert_any_call("Error fetching record pid1: 404", level="error")


def test_print_summary(capsys):
    results = [
        OutputMigrationResult("pid1", status="SUCCESS"),
        OutputMigrationResult("pid2", status="FAILED", errors=["some error"]),
        OutputMigrationResult("pid3", status="SUCCESS"),
    ]

    _print_summary(results)

    output = capsys.readouterr().out
    assert "Total: 3" in output
    assert "SUCCESS: 2" in output
    assert "FAILED: 1" in output


def test_main_creates_context_with_correct_args(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "outputs_migrate",
            "--pids",
            "pid1",
            "--system",
            "pre",
            "--login-id",
            "test@test.se",
            "--app-token",
            "token123",
            "--workers",
            "8",
        ],
    )

    cora_context_mock = MagicMock()
    monkeypatch.setattr("scripts.outputs_migrate.CoraContext", cora_context_mock)

    def fake_get(pids, workers, on_success, on_error):
        pass

    monkeypatch.setattr("scripts.outputs_migrate.get_classic_publications", fake_get)
    monkeypatch.setattr("scripts.outputs_migrate.output_migrate", MagicMock())

    ssh_tunnel_mock = MagicMock()
    ssh_tunnel_mock.return_value.__enter__ = MagicMock()
    ssh_tunnel_mock.return_value.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("scripts.outputs_migrate.SSHTunnel", ssh_tunnel_mock)

    main()

    cora_context_mock.assert_called_once_with(
        system="pre",
        login_id="test@test.se",
        app_token="token123",
        workers=8,
    )
