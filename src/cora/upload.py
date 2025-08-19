import os
import requests
import xml.etree.ElementTree as ET
from common.xml_utils import pretty_print_xml
from cora.context import Context


def upload_binary(binary_record: ET.Element, file_path: str, context: Context):
    print(f"Uploading binary file: {file_path}")

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return False

    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    request_url = upload_action_link.findtext("./url")
    assert request_url is not None, "Upload URL not found in action link"

    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                request_url,
                files={"file": file},
                headers={
                    "Authtoken": context.get_auth_token(),
                },
            )
    except (OSError, IOError) as e:
        print(f"Error reading file '{file_path}': {e}")
        return False

    print(f"Upload response: {response.status_code}")
    if response.status_code == 200:
        print("Upload successful")
        return True
    else:
        print(f"Upload failed: {response.text}")
        return False
