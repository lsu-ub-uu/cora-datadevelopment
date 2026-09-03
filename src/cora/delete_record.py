import xml.etree.ElementTree as ET
import logging
import requests
from cora.context import Context

logger = logging.getLogger(__name__)


def delete_record(record_type: str, record_id: str, context: Context):
    try:
        response = requests.delete(
            context.get_base_url() + f"{record_type}/{record_id}",
            headers={
                "authToken": context.get_auth_token(),
            },
        )

        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(
            f"❌ An error occurred while deleting record {record_type} with id {record_id}: {str(e)}"
        )
        raise e
