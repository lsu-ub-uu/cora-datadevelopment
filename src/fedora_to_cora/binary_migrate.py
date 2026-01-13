import requests
import xml.etree.ElementTree as ET
from requests_toolbelt.multipart.encoder import MultipartEncoder
from cora.context import Context
import time


def migrate_binary(binary_record: ET.Element, pid: str, file_name: str, context: Context):
    download_url = f"http://localhost:8088/fedora/get/{pid}/{file_name}"
    start_migrate = time.perf_counter()
    context.log(f"[PID {pid}] ⏳ Starting migrate file from Fedora: {download_url}")
    
    with requests.get(download_url, stream=True) as download_response:
        download_response.raise_for_status()
        multipart_data = MultipartEncoder(
            fields={
                "file": (
                    file_name,
                    download_response.raw,
                    "application/octet-stream",
                )
            }
        )

        upload_url = _get_upload_url(binary_record)

        upload_response = requests.post(
            upload_url,
            data=multipart_data,
            headers={
                "Authtoken": context.get_auth_token(),
                "Content-Type": multipart_data.content_type,
            },
            stream=True
        )
        
        if upload_response.status_code != 200:
            context.log(f"[PID {pid}] Upload failed: {upload_response.text}")
            raise UploadError(
                f"Failed to upload binary file '{file_name}': {upload_response.status_code} - {upload_response.text}"
            )
        

    end_migrate = time.perf_counter()
    migrate_time = end_migrate - start_migrate
    context.log(f"[PID {pid}] 🥳 Migrated binary file '{file_name}' from Fedora in {migrate_time:.2f} seconds")



def _get_upload_url(binary_record: ET.Element) -> str:
    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    upload_url = upload_action_link.findtext("./url")
    assert upload_url is not None, "Upload URL not found in action link"
    return upload_url


class UploadError(Exception):
    """Custom exception for upload errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UploadError: {self.message}"
