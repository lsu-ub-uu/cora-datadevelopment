import requests
import xml.etree.ElementTree as ET
from common.common_data import validateRecord_build
from logging import Logger
from typing import Tuple, List, Optional

filePath_validateBase = r"data/cora/validate/validation_order_base.xml"


def validate_record(
    record: ET.Element,
    *,
    record_type: str,
    auth_token: str,
    base_url: str,
    logger: Logger,
) -> Tuple[bool, Optional[List[str]]]:
    validate_url = base_url + "workOrder"
    headers = {
        "Content-Type": "application/vnd.cora.workorder+xml",
        "Accept": "application/vnd.cora.record+xml",
        "authToken": auth_token,
    }

    old_id = record.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    validation_order = validateRecord_build(record_type, filePath_validateBase, record)

    request_body = f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(validation_order).decode("UTF-8")}'

    response = requests.post(validate_url, data=request_body, headers=headers)

    if response.status_code != 200 or not response.text:
        logger.error(
            f"⚠️ Failed to validate {record_type} with oldId {old_id_text}: {response.status_code}."
        )
        return (False, [f"Validation failed with status {response.status_code}"])

    response_data = ET.fromstring(response.text)
    valid = response_data.find(".//valid")

    if valid is not None and valid.text == "true":
        logger.info(
            f"✅ Validation succeeded for {record_type} with oldId {old_id_text}."
        )
        return (True, None)

    errors = [msg.text for msg in response_data.findall(".//errorMessage") if msg.text]
    logger.error(
        f"❌ Validation failed for {record_type} with oldId {old_id_text}.\n\nErrors:\n - {"\n - ".join(errors)}\n"
    )
    return (False, errors)
