import requests
import xml.etree.ElementTree as ET
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common.xml_utils import pretty_print_xml
from cora.context import Context, CoraContext, MockContext
from cora.create import create_record
import time


def migrate_binary(binary_record: ET.Element, pid: str, file_name: str, context: Context):
    download_url = f"http://localhost:8088/fedora/get/{pid}/{file_name}"
    start_download = time.perf_counter()
    context.log(f"[PID {pid}] ⬇️ Starting download from Fedora: {download_url}")
    with requests.get(download_url, stream=True) as download_response:
        download_response.raise_for_status()
        content = download_response.content
    end_download = time.perf_counter()
    download_time = end_download - start_download
    context.log(f"[PID {pid}] ⬇️ Downloaded binary file '{file_name}' from Fedora in {download_time:.2f} seconds")

    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    request_url = upload_action_link.findtext("./url")
    assert request_url is not None, "Upload URL not found in action link"

    multipart_data = MultipartEncoder(
        fields={
            "file": (
                file_name,
                content,
                "application/octet-stream",
            )
        }
    )

    context.log(f"[PID {pid}] ⬆️ Starting upload to Cora for '{request_url}'")
    start_upload = time.perf_counter()
    with requests.post(
        request_url,
        data=multipart_data,
        headers={
            "Authtoken": context.get_auth_token(),
            "Content-Type": multipart_data.content_type,
        },
    ) as response:
        end_upload = time.perf_counter()
        upload_time = end_upload - start_upload

        if response.status_code == 200:
            context.log(f"[PID {pid}] ⬆️ Upload successful: {file_name} in {upload_time:.2f} seconds")
        else:
            context.log(f"[PID {pid}] Upload failed: {response.text} (after {upload_time:.2f} seconds)")
            raise UploadError(
                f"Failed to upload binary file '{file_name}': {response.status_code} - {response.text}"
            )



class UploadError(Exception):
    """Custom exception for upload errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UploadError: {self.message}"
