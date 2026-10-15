from pathlib import Path
from unittest.mock import Mock
import pytest

from fedora_to_cora import old_records_migrate
from fedora_to_cora.migrate_old_record import MigrateOldRecordResult


@pytest.fixture
def context(monkeypatch):
    context = Mock()
    monkeypatch.setattr(old_records_migrate, "CoraContext", Mock(return_value=context))
    return context


def test_migrates_all_top_level_xml_files(tmp_path, monkeypatch, context):
    for number in (1, 2, 3):
        (tmp_path / f"{number}.xml").write_text(f"<record><pid>{number}</pid></record>")
    (tmp_path / "ignored.txt").write_text("ignored")
    (tmp_path / "directory.xml").mkdir()
    migrate = Mock(side_effect=[
        MigrateOldRecordResult("CREATED", "old:1", None),
        MigrateOldRecordResult("SKIPPED", None, "Already exists"),
        MigrateOldRecordResult("FAILED", None, "Rejected"),
    ])
    monkeypatch.setattr(old_records_migrate, "old_record_migrate", migrate)

    summary = old_records_migrate.migrate_old_records(
        tmp_path, system="pre", login_id="user", app_token="token",
        workers=1, cora_url="https://example.org",
    )

    assert summary.xml_files == 3
    assert summary.counts == {"CREATED": 1, "SKIPPED": 1, "FAILED": 1}
    assert [call.args[0].findtext("pid") for call in migrate.call_args_list] == ["1", "2", "3"]
    assert all(call.args[1] is context for call in migrate.call_args_list)
    old_records_migrate.CoraContext.assert_called_once_with(
        system="pre", login_id="user", app_token="token", workers=1,
        cora_url="https://example.org",
    )


def test_empty_directory_does_not_authenticate(tmp_path, context):
    summary = old_records_migrate.migrate_old_records(tmp_path)

    assert summary.xml_files == 0
    assert summary.counts == {"CREATED": 0, "SKIPPED": 0, "FAILED": 0}
    old_records_migrate.CoraContext.assert_not_called()


@pytest.mark.parametrize("workers", [0, -1])
def test_invalid_workers(tmp_path, workers, context):
    with pytest.raises(ValueError, match="Workers must be a positive integer"):
        old_records_migrate.migrate_old_records(tmp_path, workers=workers)
    old_records_migrate.CoraContext.assert_not_called()


def test_invalid_directory(tmp_path, context):
    with pytest.raises(ValueError, match="Not a directory"):
        old_records_migrate.migrate_old_records(tmp_path / "missing")
    old_records_migrate.CoraContext.assert_not_called()


def test_context_failure_is_reported(tmp_path, monkeypatch, context):
    (tmp_path / "1.xml").write_text("<record><pid>1</pid></record>")
    old_records_migrate.CoraContext.side_effect = RuntimeError("Login failed")
    migrate = Mock()
    monkeypatch.setattr(old_records_migrate, "old_record_migrate", migrate)

    summary = old_records_migrate.migrate_old_records(tmp_path)

    assert summary.initialization_error == "Login failed"
    assert summary.outcomes == []
    migrate.assert_not_called()


@pytest.mark.parametrize("failure", ["parse", "read", "migration"])
def test_file_failure_does_not_abort_other_files(tmp_path, monkeypatch, context, failure):
    for number in (1, 2):
        (tmp_path / f"{number}.xml").write_text(f"<record><pid>{number}</pid></record>")
    if failure == "parse":
        (tmp_path / "1.xml").write_text("<broken>")
    if failure == "read":
        original_read = old_records_migrate.read_source_xml

        def read(path):
            if path.name == "1.xml":
                raise OSError("Cannot read")
            return original_read(path)

        monkeypatch.setattr(old_records_migrate, "read_source_xml", read)

    def migrate(source_record, context):
        if failure == "migration" and source_record.findtext("pid") == "1":
            raise RuntimeError("Unexpected failure")
        return MigrateOldRecordResult("CREATED", "old:2", None)

    monkeypatch.setattr(old_records_migrate, "old_record_migrate", migrate)

    summary = old_records_migrate.migrate_old_records(tmp_path, workers=2)

    assert summary.counts == {"CREATED": 1, "SKIPPED": 0, "FAILED": 1}
    failed = next(outcome for outcome in summary.outcomes if outcome.status == "FAILED")
    assert failed.xml_path == tmp_path / "1.xml"
    assert failed.error


def test_repeated_pid_is_processed_and_skipped(tmp_path, monkeypatch, context):
    for name in ("first", "second"):
        (tmp_path / f"{name}.xml").write_text("<record><pid>1</pid></record>")
    monkeypatch.setattr(old_records_migrate, "old_record_migrate", Mock(side_effect=[
        MigrateOldRecordResult("CREATED", "old:1", None),
        MigrateOldRecordResult("SKIPPED", None, "Already exists"),
    ]))

    summary = old_records_migrate.migrate_old_records(tmp_path)

    assert summary.counts == {"CREATED": 1, "SKIPPED": 1, "FAILED": 0}