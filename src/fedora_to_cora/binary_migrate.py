import requests
import os
import xml.etree.ElementTree as ET
import logging
from requests_toolbelt.multipart.encoder import MultipartEncoder
from cora.context import Context
import time

logger = logging.getLogger(__name__)


def migrate_binary(
    binary_record: ET.Element,
    pid: str,
    file_name: str,
    context: Context,
    *,
    fedora_url: str | None,
):
    fedora_url = fedora_url if fedora_url is not None else os.environ.get("FEDORA_URL")
    if not fedora_url:
        raise ValueError("FEDORA_URL is required to migrate binaries")
    download_url = f"{fedora_url}/fedora/get/{pid}/{file_name}"
    start_migrate = time.perf_counter()
    logger.info(f"[PID {pid}] ⏳ Starting migrate file from Fedora: {download_url}")

    expected_file_size = _get_expected_file_size(binary_record)
    file_size_mb = expected_file_size / (1024 * 1024)
    upload_url = _get_upload_url(binary_record)

    with requests.get(download_url, stream=True) as download_response:
        download_response.raise_for_status()
        download_response.raw.decode_content = True
        binary_stream = _ExpectedSizeReader(download_response.raw, expected_file_size)

        multipart_data = MultipartEncoder(
            fields={
                "file": (
                    file_name,
                    binary_stream,
                    "application/octet-stream",
                )
            }
        )

        with requests.post(
            upload_url,
            data=multipart_data,
            headers={
                "Authtoken": context.get_auth_token(),
                "Content-Type": multipart_data.content_type,
            },
        ) as upload_response:
            if upload_response.status_code != 200:
                logger.info(f"[PID {pid}] Upload failed: {upload_response.text}")
                raise UploadError(
                    f"Failed to upload binary file '{file_name}': {upload_response.status_code} - {upload_response.text}"
                )
        binary_stream.verify_complete()

    end_migrate = time.perf_counter()
    migrate_time = end_migrate - start_migrate
    logger.info(
        f"[PID {pid}] 🥳 Migrated binary file '{download_url}' from Fedora in {migrate_time:.2f}s (📦{file_size_mb:.2f}MB) "
    )


def _get_upload_url(binary_record: ET.Element) -> str:
    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    upload_url = upload_action_link.findtext("./url")
    assert upload_url is not None, "Upload URL not found in action link"
    return upload_url


def _get_expected_file_size(binary_record: ET.Element) -> int:
    expected_file_size = binary_record.findtext("./expectedFileSize")
    if expected_file_size is None:
        raise ValueError("Binary record is missing expectedFileSize")
    try:
        size = int(expected_file_size)
    except ValueError as error:
        raise ValueError(
            "Binary record expectedFileSize must be a non-negative integer"
        ) from error
    if size < 0:
        raise ValueError(
            "Binary record expectedFileSize must be a non-negative integer"
        )
    return size


class _ExpectedSizeReader:
    def __init__(self, stream, expected_size: int):
        self._stream = stream
        self._remaining = expected_size

    @property
    def len(self) -> int:
        return self._remaining

    def read(self, size: int = -1) -> bytes:
        if self._remaining == 0:
            return b""
        if size < 0:
            size = min(self._remaining, 64 * 1024)
        else:
            size = min(size, self._remaining)
        if size == 0:
            return b""

        chunk = self._stream.read(size)
        if not chunk:
            raise OSError("Fedora stream ended before expectedFileSize bytes")
        self._remaining -= len(chunk)
        return chunk

    def verify_complete(self):
        if self._remaining:
            raise OSError("Fedora stream ended before expectedFileSize bytes")
        if self._stream.read(1):
            raise OSError("Fedora stream exceeded expectedFileSize bytes")


class UploadError(Exception):
    """Custom exception for upload errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UploadError: {self.message}"
