import xml.etree.ElementTree as ET
import logging
from cora.context import Context
import requests

logger = logging.getLogger(__name__)


def list_records(context: Context, record_type_id: str) -> list[ET.Element]:
    request_url = f"{context.get_base_url()}{record_type_id}"
    headers = {
        "Accept": "application/vnd.cora.recordList+xml",
        "authToken": context.get_auth_token(),
    }

    try:
        response = requests.get(request_url, headers=headers)

        response.raise_for_status()

        data_list = ET.fromstring(response.text)
        return data_list.findall("./data/record")
    except Exception as e:
        logger.error(f"❌ Failed to list records of type {record_type_id}: {str(e)}")
        raise e
