import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from cora.context import MockContext
from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from fedora_to_cora.persons_migrate import (
    PersonMigrationOutcome,
    PersonMigrationSummary,
)
from fedora_to_cora.person_migrate import MigratePersonResult
from fedora_to_cora import persons_migrate
from scripts import outputs_import
from fedora_to_cora.old_records_migrate import OldRecordMigrationSummary


@pytest.fixture(autouse=True)
def mock_old_record_batch(monkeypatch):
    migrate = Mock(return_value=OldRecordMigrationSummary())
    monkeypatch.setattr(outputs_import, "migrate_old_records", migrate, raising=False)
    return migrate


@pytest.mark.parametrize("apply", [True, False])
@pytest.mark.parametrize("initialization_error", [None, "Login failed"])
def test_old_records_run_before_output_filters(
    monkeypatch, mock_old_record_batch, apply, initialization_error
):
    events = []
    mock_old_record_batch.side_effect = lambda **kwargs: events.append("old_records") or OldRecordMigrationSummary(initialization_error=initialization_error)
    monkeypatch.setattr(outputs_import, "migrate_persons", Mock(side_effect=lambda **kwargs: events.append("persons")))
    monkeypatch.setattr(outputs_import, "_read_source_record_paths", Mock(side_effect=lambda *args: events.append("read") or ["selected.xml"]))
    monkeypatch.setattr(outputs_import, "_filter_source_record_paths_by_pids", Mock(side_effect=lambda *args: events.append("filter") or []))
    monkeypatch.setattr(outputs_import, "_migrate_outputs", Mock(side_effect=lambda **kwargs: events.append("outputs") or []))
    monkeypatch.setattr(outputs_import, "_migrate_output_relations", Mock(return_value=[]))
    monkeypatch.setattr(outputs_import, "save_reports", Mock())

    outputs_import.outputs_import(
        "xml", "pre", "user", "token", 3, apply,
        limit=1, pids=["pid:1"], cora_url="https://example.org", persons=apply,
    )

    assert events == (["persons", "old_records"] if apply else []) + ["read", "filter", "outputs"]
    if apply:
        mock_old_record_batch.assert_called_once_with(
            xml_dir=Path("xml"), system="pre", login_id="user", app_token="token",
            workers=3, cora_url="https://example.org",
        )
    else:
        mock_old_record_batch.assert_not_called()


@pytest.mark.parametrize("processes", [0, -1])
def test_applied_import_rejects_invalid_processes(mock_old_record_batch, processes):
    with pytest.raises(ValueError, match="Processes must be a positive integer"):
        outputs_import.outputs_import("xml", "pre", "user", None, processes, True)
    mock_old_record_batch.assert_not_called()


def test_parse_args_defers_environment_defaults(monkeypatch):
    monkeypatch.setenv("CORA_APP_TOKEN", "test-token")
    monkeypatch.setattr(sys, "argv", ["outputs-import", "--xml-dir", "xml"])

    args = outputs_import._parse_args()

    assert (args.system, args.login_id, args.app_token) == (None, None, None)


@pytest.mark.parametrize(
    "extra", [[], ["--apply", "--processes", "0"], ["--apply", "--processes", "-1"]]
)
def test_persons_rejects_invalid_cli_options(monkeypatch, extra):
    monkeypatch.setattr(
        sys, "argv", ["outputs-import", "--xml-dir", "xml", "--persons", *extra]
    )

    with pytest.raises(SystemExit) as error:
        outputs_import._parse_args()

    assert error.value.code == 2


def test_main_forwards_persons(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["outputs-import", "--xml-dir", "xml", "--persons", "--apply"]
    )
    monkeypatch.setattr(outputs_import, "print_logo", Mock())
    monkeypatch.setattr(outputs_import, "configure_logging", Mock())
    migrate = Mock()
    monkeypatch.setattr(outputs_import, "outputs_import", migrate)

    outputs_import.main()

    assert migrate.call_args.kwargs["persons"] is True


@pytest.mark.parametrize("apply, processes", [(False, 2), (True, 0), (True, -1)])
def test_persons_validates_api_options_before_side_effects(
    monkeypatch, apply, processes
):
    migrate = Mock()
    monkeypatch.setattr(outputs_import, "migrate_persons", migrate)

    with pytest.raises(ValueError):
        outputs_import.outputs_import(
            "xml", "pre", "user", None, processes, apply, persons=True
        )

    migrate.assert_not_called()


@pytest.mark.parametrize("mode", ["success", "migration", "scan", "auth"])
def test_persons_runs_before_outputs_and_passes_summary(monkeypatch, mode):
    summary = PersonMigrationSummary()
    if mode == "migration":
        summary.outcomes = [
            PersonMigrationOutcome(
                "person:1", MigratePersonResult("FAILED", None, "Rejected")
            )
        ]
    elif mode == "scan":
        summary.xml_files = 1
        summary.scan_errors = {"broken.xml": "Invalid XML"}
    elif mode == "auth":
        summary.initialization_error = "Login failed"
    events = []
    migrate = Mock(side_effect=lambda **kwargs: events.append("persons") or summary)
    monkeypatch.setattr(outputs_import, "migrate_persons", migrate)
    read = Mock(side_effect=lambda *args: events.append("read") or ["selected.xml"])
    monkeypatch.setattr(outputs_import, "_read_source_record_paths", read)
    monkeypatch.setattr(
        outputs_import, "_filter_source_record_paths_by_pids", Mock(return_value=[])
    )
    migrate_outputs = Mock(side_effect=lambda **kwargs: events.append("outputs") or [])
    monkeypatch.setattr(outputs_import, "_migrate_outputs", migrate_outputs)
    relations = Mock(side_effect=lambda **kwargs: events.append("relations") or [])
    monkeypatch.setattr(outputs_import, "_migrate_output_relations", relations)
    reports = Mock(side_effect=lambda *args, **kwargs: events.append("reports"))
    monkeypatch.setattr(outputs_import, "save_reports", reports)

    outputs_import.outputs_import(
        "xml",
        "pre",
        "user",
        "token",
        3,
        True,
        limit=1,
        pids=["pid:1"],
        cora_url="https://example.org",
        persons=True,
    )

    assert events == ["persons", "read", "outputs", "relations", "reports"]
    migrate_outputs.assert_called_once()
    relations.assert_called_once()
    reports.assert_called_once()
    migrate.assert_called_once_with(
        xml_dir=Path("xml"),
        system="pre",
        login_id="user",
        app_token="token",
        workers=3,
        cora_url="https://example.org",
    )
    assert reports.call_args.kwargs["person_summary"] is summary


def test_person_failure_continues_outputs_and_saves_real_reports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    xml_dir = tmp_path / "xml"
    xml_dir.mkdir()
    (xml_dir / "publication.xml").write_text(
        "<publication><pid>pid:1</pid>"
        "<authorityPid>person:1</authorityPid></publication>"
    )
    monkeypatch.setattr(persons_migrate, "CoraContext", Mock())
    monkeypatch.setattr(
        persons_migrate,
        "migrate_person",
        Mock(return_value=MigratePersonResult("FAILED", None, "Rejected")),
    )
    output_result = OutputMigrationResult("pid:1", "article", status="SUCCESS")
    migrate_outputs = Mock(return_value=[output_result])
    monkeypatch.setattr(outputs_import, "_migrate_outputs", migrate_outputs)
    relations = Mock(return_value=[])
    monkeypatch.setattr(outputs_import, "_migrate_output_relations", relations)

    outputs_import.outputs_import(
        str(xml_dir), "pre", "user", None, 1, True, persons=True
    )

    migrate_outputs.assert_called_once()
    assert migrate_outputs.call_args.kwargs["source_record_paths"] == [
        str(xml_dir / "publication.xml")
    ]
    relations.assert_called_once()
    assert relations.call_args.kwargs["migration_results"] == [output_result]
    for extension in ("html", "md"):
        text = next((tmp_path / "reports").glob(f"*.{extension}")).read_text()
        assert "Person Migration" in text
        assert "person:1" in text
        assert "Rejected" in text
        assert "Successfully imported" in text
        assert "output and relation migration continued" in text
        assert "Output and relation migration not run" not in text


def test_persons_scans_entire_directory_despite_output_filters(tmp_path, monkeypatch):
    for number in (1, 2):
        (tmp_path / f"{number}.xml").write_text(
            f"<publication><pid>pid:{number}</pid>"
            f"<authorityPid>person:{number}</authorityPid></publication>"
        )
    (tmp_path / "ignored.txt").write_text("not XML")
    monkeypatch.setattr(persons_migrate, "CoraContext", Mock())
    migrate = Mock(return_value=MigratePersonResult("SKIPPED", None, "Exists"))
    monkeypatch.setattr(persons_migrate, "migrate_person", migrate)
    outputs = Mock(return_value=[])
    monkeypatch.setattr(outputs_import, "_migrate_outputs", outputs)
    monkeypatch.setattr(
        outputs_import, "_migrate_output_relations", Mock(return_value=[])
    )
    reports = Mock()
    monkeypatch.setattr(outputs_import, "save_reports", reports)

    outputs_import.outputs_import(
        str(tmp_path),
        "pre",
        "user",
        "token",
        2,
        True,
        limit=1,
        pids=["pid:missing"],
        persons=True,
    )

    assert {invocation.args[0] for invocation in migrate.call_args_list} == {
        "person:1",
        "person:2",
    }
    assert outputs.call_args.kwargs["source_record_paths"] == []
    summary = reports.call_args.kwargs["person_summary"]
    assert summary.xml_files == 2
    assert summary.counts["SKIPPED"] == 2


def test_main_resolves_environment_before_import(monkeypatch):
    monkeypatch.setenv("CORA_SYSTEM", "dev")
    monkeypatch.setenv("CORA_LOGIN_ID", "test-login")
    monkeypatch.setenv("CORA_APP_TOKEN", "test-token")
    monkeypatch.setattr(sys, "argv", ["outputs-import", "--xml-dir", "xml"])
    monkeypatch.setattr(outputs_import, "print_logo", lambda: None)
    monkeypatch.setattr(outputs_import, "configure_logging", lambda: None)
    captured = {}
    monkeypatch.setattr(
        outputs_import, "outputs_import", lambda **kwargs: captured.update(kwargs)
    )

    outputs_import.main()

    assert captured["system"] == "dev"
    assert captured["login_id"] == "test-login"
    assert captured["app_token"] is None


class _FakePool:
    test_results = []
    test_results_batches = []
    captured_iterable = None
    captured_processes = None
    captured_initargs = None
    captured_iterables = []
    captured_processes_list = []
    captured_initargs_list = []

    def __init__(self, processes, initializer, initargs):
        _FakePool.captured_processes = processes
        _FakePool.captured_initargs = initargs
        _FakePool.captured_processes_list.append(processes)
        _FakePool.captured_initargs_list.append(initargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def imap_unordered(self, worker, iterable):
        _FakePool.captured_iterable = list(iterable)
        _FakePool.captured_iterables.append(_FakePool.captured_iterable)
        if _FakePool.test_results_batches:
            return iter(_FakePool.test_results_batches.pop(0))
        return iter(_FakePool.test_results)


class _FakeTqdm:
    instances = []

    def __init__(self, total, desc):
        self.total = total
        self.desc = desc
        self.updated = 0
        self.postfixes = []
        _FakeTqdm.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def set_postfix_str(self, text):
        self.postfixes.append(text)

    def update(self, count):
        self.updated += count


def test_read_source_record_paths_applies_limit_and_filters_non_xml(tmp_path):
    with patch(
        "scripts.outputs_import.os.listdir",
        return_value=["a.xml", "ignore.txt", "b.xml"],
    ):
        result = outputs_import._read_source_record_paths(str(tmp_path), limit=1)

    assert result == [str(tmp_path / "a.xml")]


def test_filter_source_record_paths_by_pids_filters_by_record_pid(tmp_path):
    first_xml = tmp_path / "first.xml"
    first_xml.write_text("<publication><pid>diva2:111</pid></publication>")

    second_xml = tmp_path / "second.xml"
    second_xml.write_text("<publication><pid>diva2:222</pid></publication>")

    result = outputs_import._filter_source_record_paths_by_pids(
        [str(first_xml), str(second_xml)],
        ["diva2:222"],
    )

    assert result == [str(second_xml)]


@patch("scripts.outputs_import.output_migrate")
@patch("scripts.outputs_import.read_source_xml")
def test_migrate_record_reads_source_xml_from_path(
    mock_read_source_xml, mock_output_migrate
):
    source_record = ET.fromstring("<publication><pid>diva2:123</pid></publication>")
    mock_read_source_xml.return_value = source_record
    mock_output_migrate.return_value = OutputMigrationResult("diva2:123", "SUCCESS")

    outputs_import.context = MockContext()
    outputs_import.apply = False
    outputs_import.with_binaries = True
    outputs_import.fedora_url = "http://fedora.example"

    source_path = "/tmp/publication.xml"
    result = outputs_import._migrate_record(source_path)

    mock_read_source_xml.assert_called_once_with(source_path)
    mock_output_migrate.assert_called_once_with(
        source_record,
        outputs_import.context,
        False,
        with_binaries=True,
        fedora_url="http://fedora.example",
    )
    assert result.status == "SUCCESS"


@patch("scripts.outputs_import.save_reports")
@patch("scripts.outputs_import._filter_source_record_paths_by_pids")
@patch("scripts.outputs_import._read_source_record_paths")
@patch("scripts.outputs_import.tqdm", side_effect=lambda **kwargs: _FakeTqdm(**kwargs))
@patch("scripts.outputs_import.Pool", _FakePool)
def test_outputs_import_orchestrates_loading_filtering_pool_and_reports(
    mock_tqdm,
    mock_read_source_record_paths,
    mock_filter_source_record_paths_by_pids,
    mock_save_reports,
):
    _FakeTqdm.instances = []
    _FakePool.captured_iterables = []
    _FakePool.captured_processes_list = []
    _FakePool.captured_initargs_list = []
    _FakePool.test_results_batches = [
        [
            OutputMigrationResult("diva2:1", "SUCCESS"),
            OutputMigrationResult("diva2:2", "FAILED", errors=["x"]),
        ],
        [
            OutputRelationMigrationResult(
                status="UPDATED", pid="diva2:1", cora_id="1", error=None
            ),
            OutputRelationMigrationResult(
                status="FAILED", pid="diva2:2", cora_id="2", error="relation"
            ),
        ],
    ]

    mock_read_source_record_paths.return_value = ["a.xml", "b.xml", "c.xml"]
    mock_filter_source_record_paths_by_pids.return_value = ["b.xml", "c.xml"]

    outputs_import.outputs_import(
        xml_dir="/tmp/xml",
        system="pre",
        login_id="user",
        app_token="token",
        processes=2,
        apply=False,
        limit=10,
        binaries=False,
        pids=["diva2:2"],
        fedora_url="",
        cora_url="",
    )

    mock_read_source_record_paths.assert_called_once_with("/tmp/xml", 10)
    mock_filter_source_record_paths_by_pids.assert_called_once_with(
        ["a.xml", "b.xml", "c.xml"], ["diva2:2"]
    )
    assert _FakePool.captured_processes == 2
    assert _FakePool.captured_iterables[0] == ["b.xml", "c.xml"]
    assert _FakePool.captured_initargs_list[0] == (
        "pre",
        "user",
        "token",
        "",
        False,
        False,
        "",
    )
    assert _FakePool.captured_initargs_list[1] == ("pre", "user", "token", "")
    assert [result.pid for result in _FakePool.captured_iterables[1]] == [
        "diva2:1",
        "diva2:2",
    ]
    assert _FakeTqdm.instances[0].total == 2
    assert _FakeTqdm.instances[0].updated == 2
    assert "✅ 1" in _FakeTqdm.instances[0].postfixes[-1]
    assert "❌ 1" in _FakeTqdm.instances[0].postfixes[-1]
    assert _FakeTqdm.instances[1].desc == "Importing output relations"

    results_arg = mock_save_reports.call_args.args[0]
    assert [result.status for result in results_arg] == ["SUCCESS", "FAILED"]
    save_reports_kwargs = mock_save_reports.call_args.kwargs
    relation_results = save_reports_kwargs.pop("relation_results")
    assert save_reports_kwargs == {
        "xml_dir": "/tmp/xml",
        "system": "pre",
        "apply": False,
        "binaries": False,
        "cora_url": "",
        "output_dir": "reports",
        "person_summary": None,
    }
    assert [(r.status, r.pid, r.error) for r in relation_results] == [
        ("UPDATED", "diva2:1", None),
        ("FAILED", "diva2:2", "relation"),
    ]


def test_migrate_record_raises_assertion_when_context_not_initialized():
    outputs_import.context = None

    with pytest.raises(
        AssertionError,
        match="Context must be initialized before migrating records",
    ):
        outputs_import._migrate_record("/tmp/publication.xml")


def test_filter_source_record_paths_by_pids_returns_empty_for_empty_pid_list(tmp_path):
    xml_file = tmp_path / "publication.xml"
    xml_file.write_text("<publication><pid>diva2:111</pid></publication>")

    result = outputs_import._filter_source_record_paths_by_pids([str(xml_file)], [])

    assert result == []


def test_filter_source_record_paths_by_pids_ignores_missing_pid_and_duplicate_input_pids(
    tmp_path,
):
    with_pid = tmp_path / "with_pid.xml"
    with_pid.write_text("<publication><pid>diva2:222</pid></publication>")

    without_pid = tmp_path / "without_pid.xml"
    without_pid.write_text("<publication><title>No PID</title></publication>")

    result = outputs_import._filter_source_record_paths_by_pids(
        [str(with_pid), str(without_pid)],
        ["diva2:222", "diva2:222"],
    )

    assert result == [str(with_pid)]


def test_filter_source_record_paths_by_pids_raises_for_malformed_xml(tmp_path):
    malformed_xml = tmp_path / "broken.xml"
    malformed_xml.write_text("<publication><pid>diva2:1</pid>")

    with pytest.raises(ET.ParseError):
        outputs_import._filter_source_record_paths_by_pids(
            [str(malformed_xml)],
            ["diva2:1"],
        )


@patch("scripts.outputs_import.read_source_xml", side_effect=ET.ParseError("bad xml"))
def test_migrate_record_propagates_xml_parse_error(mock_read_source_xml):
    outputs_import.context = MockContext()

    with pytest.raises(ET.ParseError):
        outputs_import._migrate_record("/tmp/broken.xml")

    mock_read_source_xml.assert_called_once_with("/tmp/broken.xml")


@patch("scripts.outputs_import.save_reports")
@patch("scripts.outputs_import._filter_source_record_paths_by_pids")
@patch("scripts.outputs_import._read_source_record_paths")
@patch("scripts.outputs_import.tqdm", side_effect=lambda **kwargs: _FakeTqdm(**kwargs))
@patch("scripts.outputs_import.Pool", _FakePool)
def test_outputs_import_preserves_reporting_contract_without_pid_filter(
    mock_tqdm,
    mock_read_source_record_paths,
    mock_filter_source_record_paths_by_pids,
    mock_save_reports,
):
    _FakeTqdm.instances = []
    _FakePool.captured_iterables = []
    _FakePool.captured_processes_list = []
    _FakePool.captured_initargs_list = []
    _FakePool.test_results_batches = [
        [
            OutputMigrationResult("diva2:1", "SUCCESS"),
            OutputMigrationResult("diva2:2", "CLASSIC_QUALITY", errors=["warning"]),
        ],
        [
            OutputRelationMigrationResult(
                status="UPDATED", pid="diva2:1", cora_id="1", error=None
            ),
            OutputRelationMigrationResult(
                status="NO_RELATIONS", pid="diva2:2", cora_id="2", error=None
            ),
        ],
    ]

    mock_read_source_record_paths.return_value = ["a.xml", "b.xml"]

    outputs_import.outputs_import(
        xml_dir="/tmp/xml",
        system="pre",
        login_id="user",
        app_token="token",
        processes=4,
        apply=False,
        limit=None,
        binaries=False,
        pids=None,
        fedora_url="",
        cora_url="",
    )

    mock_filter_source_record_paths_by_pids.assert_not_called()
    assert _FakePool.captured_iterables[0] == ["a.xml", "b.xml"]
    assert _FakeTqdm.instances[0].total == 2
    assert _FakeTqdm.instances[0].updated == 2

    results_arg = mock_save_reports.call_args.args[0]
    assert [result.status for result in results_arg] == ["SUCCESS", "CLASSIC_QUALITY"]
