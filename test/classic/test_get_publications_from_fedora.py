from xml.etree import ElementTree as ET

import pytest
from classic.get_publications_from_fedora import get_publications_from_fedora
from common.test_helper import assert_equal_for_xml_and_xml_string
from fabric import Connection
from unittest.mock import MagicMock, patch


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_get_publications_from_fedora(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    pid2 = "another-pid"
    pid3 = "third-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
    )
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid2}/MODEL_NOREF",
        text=f"<publication><pid>{pid2}</pid></publication>",
    )
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid3}/MODEL_NOREF",
        text=f"<publication><pid>{pid3}</pid></publication>",
    )

    mock_connection: Connection = MagicMock(spec=Connection)

    result = get_publications_from_fedora(
        ssh_connection=mock_connection,
        pids=[pid1, pid2, pid3],
        dirname="some-dir",
        workers=1,
    )

    assert mock_save_to_file.call_count == 3

    assert mock_download_attachments.call_count == 3

    assert_equal_for_xml_and_xml_string(
        result[0], "<publication><pid>some-pid</pid></publication>"
    )
    assert_equal_for_xml_and_xml_string(
        result[1], "<publication><pid>another-pid</pid></publication>"
    )
    assert_equal_for_xml_and_xml_string(
        result[2], "<publication><pid>third-pid</pid></publication>"
    )


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_get_publications_from_fedora_saves_to_file(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
    )

    mock_connection: Connection = MagicMock(spec=Connection)

    result = get_publications_from_fedora(
        ssh_connection=mock_connection,
        pids=[pid1],
        dirname="some-dir",
        workers=1,
    )

    assert_equal_for_xml_and_xml_string(
        mock_save_to_file.mock_calls[0].args[0],
        "<publication><pid>some-pid</pid></publication>",
    )

    assert mock_save_to_file.mock_calls[0].args[1] == f"some-dir/{pid1}.xml"


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_get_publications_from_fedora_downloads_attachments(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
    )

    mock_connection: Connection = MagicMock(spec=Connection)

    result = get_publications_from_fedora(
        ssh_connection=mock_connection,
        pids=[pid1],
        dirname="some-dir",
        workers=1,
    )

    assert_equal_for_xml_and_xml_string(
        mock_download_attachments.mock_calls[0].args[0],
        "<publication><pid>some-pid</pid></publication>",
    )

    assert mock_download_attachments.mock_calls[0].args[1] == pid1
    assert mock_download_attachments.mock_calls[0].args[2] == "some-dir"


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_raises_exception_when_error_getting_data(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
        status_code=500,
    )

    mock_connection: Connection = MagicMock(spec=Connection)

    with pytest.raises(
        Exception,
        match="Error fetching record some-pid: 500 - <publication><pid>some-pid</pid></publication>",
    ):
        get_publications_from_fedora(
            ssh_connection=mock_connection,
            pids=[pid1],
            dirname="some-dir",
            workers=1,
        )


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_raises_exception_when_error_saving_to_file(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
    )

    mock_save_to_file.side_effect = Exception("Failed to save file")

    mock_connection: Connection = MagicMock(spec=Connection)

    with pytest.raises(
        Exception,
        match="Failed to save file",
    ):
        get_publications_from_fedora(
            ssh_connection=mock_connection,
            pids=[pid1],
            dirname="some-dir",
            workers=1,
        )


@patch("classic.get_publications_from_fedora.save_to_file")
@patch("classic.get_publications_from_fedora._download_attachments")
def test_raises_exception_when_error_downloading_attachments(
    mock_download_attachments, mock_save_to_file, requests_mock
):
    pid1 = "some-pid"
    requests_mock.get(
        f"http://localhost:8088/fedora/get/{pid1}/MODEL_NOREF",
        text=f"<publication><pid>{pid1}</pid></publication>",
    )

    mock_download_attachments.side_effect = Exception("Failed to download attachments")

    mock_connection: Connection = MagicMock(spec=Connection)

    with pytest.raises(
        Exception,
        match="Failed to download attachments",
    ):
        get_publications_from_fedora(
            ssh_connection=mock_connection,
            pids=[pid1],
            dirname="some-dir",
            workers=1,
        )
