import requests
import xml.etree.ElementTree as ET
from cora.context import Context


def delete_record(record: ET.Element, context: Context):
    request_url = record.findtext("./actionLinks/delete/url")
    assert request_url is not None, "Delete URL not found in action link"

    response = requests.delete(
        request_url, headers={"Authtoken": context.get_auth_token()}
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to delete record: {response.status_code} - {response.text}"
        )
