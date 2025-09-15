from datetime import datetime
from xml.etree import ElementTree as ET
from unittest.mock import MagicMock, call, patch
import pytest
from fedora_to_cora.export_publications_from_fedora import (
    export_publications_from_fedora,
)


@patch("fedora_to_cora.export_publications_from_fedora._get_now")
@patch("fedora_to_cora.export_publications_from_fedora.diva_ssh_connection")
@patch("fedora_to_cora.export_publications_from_fedora.get_publications_from_fedora")
@patch("fedora_to_cora.export_publications_from_fedora.get_pids_for_domain")
@patch("fedora_to_cora.export_publications_from_fedora.RunRotatingLogger")
def test_export_publications_from_fedora(
    mock_logger,
    mock_get_pids,
    mock_get_publications,
    mock_diva_ssh_connection,
    mock_get_now,
):
    mock_get_pids.return_value = ["123", "456", "789"]
    mock_get_now.return_value = datetime(2023, 1, 1, 12, 0, 0)

    mock_ssh_connection = MagicMock()
    mock_diva_ssh_connection.return_value.__enter__.return_value = mock_ssh_connection

    export_publications_from_fedora("varldskulturmuseerna")

    mock_get_pids.assert_called_once_with(mock_ssh_connection, "varldskulturmuseerna")

    mock_get_publications.assert_called_once()
    call_args = mock_get_publications.call_args
    assert call_args.args[0] == mock_ssh_connection  # ssh_connection
    assert call_args.args[1] == ["123", "456", "789"]  # pids
    assert call_args.kwargs["workers"] == 16
    assert (
        call_args.kwargs["dirname"]
        == "data/fedora_xml/varldskulturmuseerna/2023-01-01T12:00:00"
    )


@patch("fedora_to_cora.export_publications_from_fedora.diva_ssh_connection")
@patch("fedora_to_cora.export_publications_from_fedora.get_publications_from_fedora")
@patch("fedora_to_cora.export_publications_from_fedora.get_pids_for_domain")
@patch("fedora_to_cora.export_publications_from_fedora.RunRotatingLogger")
def test_get_pids_failed(
    mock_logger, mock_get_pids, mock_get_publications, mock_ssh_connection
):
    mock_get_pids.side_effect = Exception("Failed to get PIDs")

    with pytest.raises(Exception, match="Failed to get PIDs"):
        export_publications_from_fedora("varldskulturmuseerna")

    mock_get_publications.assert_not_called()


@patch("fedora_to_cora.export_publications_from_fedora.diva_ssh_connection")
@patch("fedora_to_cora.export_publications_from_fedora.get_publications_from_fedora")
@patch("fedora_to_cora.export_publications_from_fedora.get_pids_for_domain")
@patch("fedora_to_cora.export_publications_from_fedora.RunRotatingLogger")
def test_get_publications_failed(
    mock_logger, mock_get_pids, mock_get_publications, mock_ssh_connection
):
    mock_get_pids.return_value = ["123", "456", "789"]
    mock_get_publications.side_effect = Exception("Failed to get publications")

    with pytest.raises(Exception, match="Failed to get publications"):
        export_publications_from_fedora("varldskulturmuseerna")
