import xml.etree.ElementTree as ET
from cora.context import Context
import requests


def get_record(context: Context, record_type: str, record_id: str) -> ET.Element:
    request_url = f"{context.get_base_url()}{record_type}/{record_id}"
    headers = {
        "Accept": "application/vnd.cora.record+xml",
        "authToken": context.get_auth_token(),
    }

    try:
        response = requests.get(request_url, headers=headers)

        response.raise_for_status()

        return ET.fromstring(response.text)
    except Exception as e:
        context.log(
            f"❌ An error occurred while fetching record {record_type} with id {record_id}: {str(e)}",
            "error",
        )
        raise e
