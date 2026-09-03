import requests
import logging
from cora.context import Context
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def get_incoming_links(context: Context, record_type: str, record_id: str):
    request_url = f"{context.get_base_url()}{record_type}/{record_id}/incomingLinks"
    headers = {
        "Accept": "application/vnd.cora.recordList+xml",
        "authToken": context.get_auth_token(),
    }

    try:
        response = requests.get(request_url, headers=headers)

        response.raise_for_status()

        response_data = ET.fromstring(response.text)

        return response_data.findall("./data/recordToRecordLink")
    except Exception as e:
        logger.error(
            f"❌ An error occurred while fetching incoming links for {record_type} with id {record_id}: {str(e)}"
        )
        raise e
