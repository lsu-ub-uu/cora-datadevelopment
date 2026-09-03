from datetime import datetime
from xml.etree import ElementTree as ET
from unittest.mock import MagicMock, call
import pytest
from fedora_to_cora.export_publications_from_fedora import (
    export_publications_from_fedora,
)


def test_export_publications_from_fedora(monkeypatch, caplog):
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)

    mock_publication = ET.Element("publication")
    get_classic_publications_mock = MagicMock()
    get_classic_publications_mock.side_effect = (
        lambda pids, workers, on_success, on_error, **kwargs: [
            on_success(pid, mock_publication) for pid in pids
        ]
    )
    monkeypatch.setattr(
        "fedora_to_cora.export_publications_from_fedora.get_classic_publications",
        get_classic_publications_mock,
    )

    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)
    monkeypatch.setattr(
        "fedora_to_cora.export_publications_from_fedora._get_now",
        lambda: datetime(2023, 1, 1, 12, 0, 0),
    )

    export_publications_from_fedora(
        "varldskulturmuseerna",
        solr_url="http://solr:8080/solr",
        fedora_url="http://fedora:8088",
    )

    assert get_pids_for_domain_mock.call_count == 1

    assert get_classic_publications_mock.call_count == 1
    assert get_classic_publications_mock.call_args[0][0] == ["123", "456", "789"]
    assert get_classic_publications_mock.call_args[0][1] == 16  # workers

    assert (
        call(
            mock_publication,
            "data/fedora_xml/varldskulturmuseerna/2023-01-01T12:00:00/123.xml",
        )
        in save_to_file_mock.mock_calls
    )
    assert (
        call(
            mock_publication,
            "data/fedora_xml/varldskulturmuseerna/2023-01-01T12:00:00/456.xml",
        )
        in save_to_file_mock.mock_calls
    )
    assert (
        call(
            mock_publication,
            "data/fedora_xml/varldskulturmuseerna/2023-01-01T12:00:00/789.xml",
        )
        in save_to_file_mock.mock_calls
    )

    assert (
        "--- Successfully imported 3 publications to data/fedora_xml/varldskulturmuseerna/2023-01-01T12:00:00 ---"
        in caplog.messages
    )


def test_get_pids_failed(monkeypatch):
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)
    get_pids_for_domain_mock.side_effect = Exception("Failed to get PIDs")
    get_classic_publications_mock, _ = _set_up_get_classic_publications_mock(
        monkeypatch
    )
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)

    with pytest.raises(Exception, match="Failed to get PIDs"):
        export_publications_from_fedora(
            "varldskulturmuseerna",
            solr_url="http://solr:8080/solr",
            fedora_url="http://fedora:8088",
        )

    assert get_pids_for_domain_mock.call_count == 1
    assert get_classic_publications_mock.call_count == 0
    assert save_to_file_mock.call_count == 0


def test_get_classic_publications_failed(monkeypatch):
    get_pids_for_domain_mock = _set_up_get_pids_mock(monkeypatch)
    _set_up_get_classic_publications_mock(monkeypatch, error=True)
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)

    export_publications_from_fedora(
        "varldskulturmuseerna",
        solr_url="http://solr:8080/solr",
        fedora_url="http://fedora:8088",
    )

    assert get_pids_for_domain_mock.call_count == 1
    assert save_to_file_mock.call_count == 0


def test_save_to_file_failed(monkeypatch):
    _set_up_get_pids_mock(monkeypatch)
    _set_up_get_classic_publications_mock(monkeypatch)
    save_to_file_mock = _set_up_save_to_file_mock(monkeypatch)
    save_to_file_mock.side_effect = (Exception("Failed to save file"),)

    export_publications_from_fedora(
        "varldskulturmuseerna",
        solr_url="http://solr:8080/solr",
        fedora_url="http://fedora:8088",
    )
    # Nothing happens


def _set_up_get_pids_mock(monkeypatch):
    get_pids_for_domain_mock = MagicMock(return_value=["123", "456", "789"])
    monkeypatch.setattr(
        "fedora_to_cora.export_publications_from_fedora.get_pids_for_domain",
        get_pids_for_domain_mock,
    )
    return get_pids_for_domain_mock


def _set_up_get_classic_publications_mock(monkeypatch, error=False):
    mock_publication = ET.Element("publication")
    get_classic_publications_mock = MagicMock()
    get_classic_publications_mock.side_effect = (
        lambda pids, workers, on_success, on_error, **kwargs: [
            (
                on_error(f"Failed to get publication {pid}")
                if error
                else on_success(pid, mock_publication)
            )
            for pid in pids
        ]
    )
    monkeypatch.setattr(
        "fedora_to_cora.export_publications_from_fedora.get_classic_publications",
        get_classic_publications_mock,
    )
    return get_classic_publications_mock, mock_publication


def _set_up_save_to_file_mock(monkeypatch):
    save_to_file_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.export_publications_from_fedora.save_to_file", save_to_file_mock
    )
    return save_to_file_mock


def _set_up_download_attachments_mock(monkeypatch):
    download_attachments_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.import_publications_from_fedora.download_attachments",
        download_attachments_mock,
    )
    return download_attachments_mock
