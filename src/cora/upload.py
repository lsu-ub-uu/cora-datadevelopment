import os
import requests
import xml.etree.ElementTree as ET
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common.xml_utils import pretty_print_xml
from cora.context import Context


def upload_binary(binary_record: ET.Element, file_path: str, context: Context):
    if not os.path.exists(file_path):
        context.log(f"Error: File '{file_path}' does not exist", level="error")
        raise UploadError(f"File '{file_path}' does not exist")

    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    request_url = upload_action_link.findtext("./url")
    assert request_url is not None, "Upload URL not found in action link"

    try:
        with open(file_path, "rb") as file:
            multipart_data = MultipartEncoder(
                fields={
                    "file": (
                        os.path.basename(file_path),
                        file,
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
    except (OSError, IOError) as e:
        context.log(f"Error reading file '{file_path}': {e}", level="error")
        raise UploadError(f"Failed to read file '{file_path}': {e}")

    if response.status_code == 200:
        context.log(f"Upload successful: {file_path}")
    else:
        context.log(f"Upload failed: {response.text}", level="error")
        raise UploadError(
            f"Failed to upload binary file '{file_path}': {response.status_code} - {response.text}"
        )


class UploadError(Exception):
    """Custom exception for upload errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UploadError: {self.message}"
