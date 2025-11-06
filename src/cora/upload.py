import os
import requests
import xml.etree.ElementTree as ET
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common.xml_utils import pretty_print_xml
from cora.context import Context


def upload_binary(
    binary_record: ET.Element, pid: str, file_name: str, context: Context
):

    download_url = f"http://localhost:8080/fedora/get/{pid}/{file_name}"

    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    request_url = upload_action_link.findtext("./url")
    assert request_url is not None, "Upload URL not found in action link"

    try:
        download_response = requests.get(download_url)
        download_response.raise_for_status()

        multipart_data = MultipartEncoder(
            fields={
                "file": (
                    file_name,
                    download_response.content,
                    "application/octet-stream",
                )
            }
        )

        response = requests.post(
            request_url,
            data=multipart_data,
            headers={
                "Authtoken": context.get_auth_token(),
                "Content-Type": multipart_data.content_type,
            },
        )
    except requests.RequestException as e:
        context.log(f"Error downloading file from '{download_url}': {e}", level="error")
        raise UploadError(f"Failed to download file from '{download_url}': {e}")

    if response.status_code == 200:
        context.log(f"Upload successful: {file_name} (downloaded from {download_url})")
    else:
        context.log(f"Upload failed: {response.text}", level="error")
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
