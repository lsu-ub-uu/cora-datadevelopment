from xml.etree import ElementTree as ET
from unittest.mock import MagicMock, call
import pytest
from fedora_to_cora.import_publications_from_fedora import (
    import_publications_from_fedora,
)


def test_import_publications_from_fedora(monkeypatch):
    logger_mock = _set_up_logger_mock(monkeypatch)
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)
    get_record_by_pid_mock, mock_publication = _set_up_get_record_mock(monkeypatch)
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)
    # download_attachments_mock = _set_up_download_attachments_mock(monkeypatch)

    import_publications_from_fedora("varldskulturmuseerna")

    assert get_pids_for_domain_mock.call_count == 1

    assert call("123") in get_record_by_pid_mock.mock_calls
    assert call("456") in get_record_by_pid_mock.mock_calls
    assert call("789") in get_record_by_pid_mock.mock_calls

    assert (
        call(mock_publication, "varldskulturmuseerna_123.xml")
        in save_to_file_mock.mock_calls
    )
    assert (
        call(mock_publication, "varldskulturmuseerna_456.xml")
        in save_to_file_mock.mock_calls
    )
    assert (
        call(mock_publication, "varldskulturmuseerna_789.xml")
        in save_to_file_mock.mock_calls
    )

    #  assert download_attachments_mock.call_count == 3

    assert logger_mock.info.mock_calls == [
        call(
            "==== Begin importing publications from Fedora ====\n==== domain=varldskulturmuseerna ====\n=================================================="
        ),
        call("--- Successfully imported 3 publications to file ---"),
    ]


def test_get_pids_failed(monkeypatch):
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)
    get_pids_for_domain_mock.side_effect = Exception("Failed to get PIDs")
    get_record_by_pid_mock, _ = _set_up_get_record_mock(monkeypatch)
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)

    with pytest.raises(Exception, match="Failed to get PIDs"):
        import_publications_from_fedora("varldskulturmuseerna")

    assert get_pids_for_domain_mock.call_count == 1
    assert get_record_by_pid_mock.call_count == 0
    assert save_to_file_mock.call_count == 0


def test_get_record_failed(monkeypatch):
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)
    get_record_by_pid_mock, _ = _set_up_get_record_mock(monkeypatch)
    get_record_by_pid_mock.side_effect = (Exception("Failed to get publication"),)

    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)

    with pytest.raises(Exception, match="Failed to get publication"):
        import_publications_from_fedora("varldskulturmuseerna")

    assert get_pids_for_domain_mock.call_count == 1
    assert save_to_file_mock.call_count == 0


def test_save_to_file_failed(monkeypatch):
    _set_up_get_pids_mock(monkeypatch)
    _set_up_get_record_mock(monkeypatch)
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)
    save_to_file_mock.side_effect = (Exception("Failed to save file"),)

    with pytest.raises(Exception, match="Failed to save file"):
        import_publications_from_fedora("varldskulturmuseerna")


def _set_up_get_pids_mock(monkeypatch):
    get_pids_for_domain_mock = MagicMock(return_value=["123", "456", "789"])
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.get_pids_for_domain",
        get_pids_for_domain_mock,
    )
    return get_pids_for_domain_mock


def _set_up_get_record_mock(monkeypatch):
    mock_publication = ET.Element("publication")
    get_record_by_pid_mock = MagicMock(return_value=mock_publication)
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.get_record_by_pid",
        get_record_by_pid_mock,
    )
    return get_record_by_pid_mock, mock_publication


def _set_up_save_to_file_mock(monkeypatch):
    save_to_file_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.save_to_file", save_to_file_mock
    )
    return save_to_file_mock


def _set_up_logger_mock(monkeypatch):
    logger_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.RunRotatingLogger.get",
        MagicMock(return_value=logger_mock),
    )
    return logger_mock


def _set_up_download_attachments_mock(monkeypatch):
    download_attachments_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.download_attachments",
        download_attachments_mock,
    )
    return download_attachments_mock
