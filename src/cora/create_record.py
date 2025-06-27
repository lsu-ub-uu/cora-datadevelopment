import requests
import xml.etree.ElementTree as ET
from common.common_data import validateRecord_build
from logging import Logger
from typing import Tuple, List, Optional


def create_record(
    record: ET.Element,
    *,
    record_type: str,
    auth_token: str,
    base_url: str,
    logger: Logger,
) -> Tuple[bool, Optional[List[str]]]:

    old_id = record.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    request_body = (
        f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(record).decode("UTF-8")}'
    )

    response = requests.post(
        f"{base_url}{record_type}",
        headers={
            "Authtoken": auth_token,
            "Content-Type": "application/vnd.cora.recordgroup+xml",
            "Accept": "application/vnd.cora.record+xml",
        },
        data=request_body,
    )

    if response.status_code == 201:
        logger.info(f"✅ Record created successfully: {old_id_text}")
        return True, None

    logger.error(
        f"❌ Failed to create record for {record_type} with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n"
    )
    return False, [f"Failed to create record with status {response.status_code}"]
