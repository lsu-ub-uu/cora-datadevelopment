import xml.etree.ElementTree as ET
from unittest.mock import patch
import pytest

from cora.context import MockContext
from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts import outputs_import


class _FakePool:
    test_results = []
    captured_iterable = None
    captured_processes = None
    captured_initargs = None

    def __init__(self, processes, initializer, initargs):
        _FakePool.captured_processes = processes
        _FakePool.captured_initargs = initargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def imap_unordered(self, worker, iterable):
        _FakePool.captured_iterable = list(iterable)
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


@patch("scripts.outputs_import._save_reports")
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
    _FakePool.test_results = [
        OutputMigrationResult("diva2:1", "SUCCESS"),
        OutputMigrationResult("diva2:2", "FAILED", errors=["x"]),
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
    assert _FakePool.captured_iterable == ["b.xml", "c.xml"]
    assert _FakeTqdm.instances[0].total == 2
    assert _FakeTqdm.instances[0].updated == 2
    assert "✅ 1" in _FakeTqdm.instances[0].postfixes[-1]
    assert "❌ 1" in _FakeTqdm.instances[0].postfixes[-1]

    results_arg = mock_save_reports.call_args.args[0]
    assert [result.status for result in results_arg] == ["SUCCESS", "FAILED"]
    assert mock_save_reports.call_args.kwargs == {
        "xml_dir": "/tmp/xml",
        "system": "pre",
        "output_dir": "reports",
    }


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


@patch("scripts.outputs_import._save_reports")
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
    _FakePool.test_results = [
        OutputMigrationResult("diva2:1", "SUCCESS"),
        OutputMigrationResult("diva2:2", "CLASSIC_QUALITY", errors=["warning"]),
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
    assert _FakePool.captured_iterable == ["a.xml", "b.xml"]
    assert _FakeTqdm.instances[0].total == 2
    assert _FakeTqdm.instances[0].updated == 2

    results_arg = mock_save_reports.call_args.args[0]
    assert [result.status for result in results_arg] == ["SUCCESS", "CLASSIC_QUALITY"]
