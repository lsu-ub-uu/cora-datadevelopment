from unittest.mock import MagicMock
import pytest
import requests_mock
import xml.etree.ElementTree as ET
from cora.upload import UploadError, upload_binary
from cora.context import MockContext


def test_upload_url_action_link_not_found(monkeypatch):
    monkeypatch.setattr(
        "os.path.exists",
        lambda x: True,
    )

    binary_record = ET.Element("binary")
    with pytest.raises(
        AssertionError, match="Upload action link not found in binary record"
    ):
        upload_binary(
            binary_record,
            file_name="test_file.txt",
            data=MagicMock(),
            context=MockContext(),
        )


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
        upload_binary(
            binary_record,
            file_name="test_file.txt",
            data=MagicMock(),
            context=MockContext(),
        )


def test_successful_upload():
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

    test_data = b"test file content"
    test_context = MockContext(auth_token="test-auth-token")

    with requests_mock.Mocker() as mocker:
        mocker.post("http://example.com/upload", text="OK", status_code=200)

        upload_binary(
            binary_record,
            file_name="test_file.txt",
            data=test_data,
            context=test_context,
        )

        assert mocker.call_count == 1
        request = mocker.request_history[0]

        assert request.url == "http://example.com/upload"
        assert request.method == "POST"
        assert "Authtoken" in request.headers
        assert request.headers["Authtoken"] == "test-auth-token"
        assert "Content-Type" in request.headers
        assert request.headers["Content-Type"].startswith("multipart/form-data")

        body_str = request.body.read().decode("utf-8", errors="ignore")
        assert "test_file.txt" in body_str
        assert "test file content" in body_str
        assert "application/octet-stream" in body_str
