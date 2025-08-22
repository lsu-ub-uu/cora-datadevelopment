from unittest.mock import MagicMock
import pytest
import xml.etree.ElementTree as ET
from cora.upload import UploadError, upload_binary
from cora.context import MockContext


def test_upload_binary_file_not_found(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: False,
    )
    binary_record = ET.fromstring(
        """
        <binary>
            <actionLinks>
                <upload>
                    <url>http://example.com/upload</url>
                </upload>
            </actionLinks>
        </binary>"""
    )
    with pytest.raises(
        UploadError, match="File 'non_existent_file.txt' does not exist"
    ):
        upload_binary(binary_record, "non_existent_file.txt", MockContext())


def test_upload_url_action_link_not_found(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: True,
    )

    binary_record = ET.Element("binary")
    with pytest.raises(
        AssertionError, match="Upload action link not found in binary record"
    ):
        upload_binary(binary_record, "test_file.txt", MockContext())


def test_error_reading_file(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: True,
    )
    monkeypatch.setattr(
        "builtins.open",
        lambda x, y: (_ for _ in ()).throw(OSError("File read error")),
    )

    binary_record = ET.fromstring(
        """
        <binary>
            <actionLinks>
                <upload>
                    <url>http://example.com/upload</url>
                </upload>
            </actionLinks>
        </binary>"""
    )

    with pytest.raises(UploadError, match="Failed to read file 'test_file.txt'"):
        upload_binary(binary_record, "test_file.txt", MockContext())


def test_error_uploading_file(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: True,
    )
    monkeypatch.setattr(
        "builtins.open",
        MagicMock(),
    )

    mock_encoder = MagicMock()
    mock_encoder.content_type = "multipart/form-data; boundary=something"
    monkeypatch.setattr(
        "cora.upload.MultipartEncoder",
        MagicMock(return_value=mock_encoder),
    )

    monkeypatch.setattr(
        "requests.post",
        MagicMock(
            return_value=MagicMock(status_code=500, text="Internal Server Error")
        ),
    )

    binary_record = ET.fromstring(
        """
        <binary>
            <actionLinks>
                <upload>
                    <url>http://example.com/upload</url>
                </upload>
            </actionLinks>
        </binary>"""
    )

    with pytest.raises(
        UploadError, match="Failed to upload binary file 'test_file.txt'"
    ):
        upload_binary(binary_record, "test_file.txt", MockContext())


def test_successful_upload(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: True,
    )
    monkeypatch.setattr(
        "builtins.open",
        MagicMock(),
    )

    mock_encoder = MagicMock()
    mock_encoder.content_type = "multipart/form-data; boundary=something"
    monkeypatch.setattr(
        "cora.upload.MultipartEncoder",
        MagicMock(return_value=mock_encoder),
    )

    monkeypatch.setattr(
        "requests.post",
        MagicMock(return_value=MagicMock(status_code=200, text="OK")),
    )

    binary_record = ET.fromstring(
        """
        <binary>
            <actionLinks>
                <upload>
                    <url>http://example.com/upload</url>
                </upload>
            </actionLinks>
        </binary>"""
    )

    upload_binary(binary_record, "test_file.txt", MockContext())
