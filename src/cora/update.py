import requests
import xml.etree.ElementTree as ET
from typing import Tuple, List, Optional
from cora.context import Context
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml


class UpdateRecordResult:
    def __init__(
        self,
        success: bool,
        error: Optional[str] = None,
        record_id: Optional[str] = None,
        response_data: Optional[ET.Element] = None,
    ):
        self.success = success
        self.record_id = record_id
        self.error = error
        self.response_data = response_data


def update_record(
    record: ET.Element,
    context: Context,
) -> UpdateRecordResult:
    """Updates a Cora record from the given XML element.

    :param updated_record: The XML element representing the updated record data.
    :param record_type: The type of the record to update (e.g., "diva-output").
    :param record_id: The ID of the record to update.
    :param context: The Cora context containing authentication and configuration information.

    :return: A CreateRecordResult object containing the success status, record ID (if successful), and any error messages.
    """
    [request_url, content_type, accept, data_group] = _parse_record(record)

    old_id = data_group.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    request_body = f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(data_group).decode("UTF-8")}'
    try:
        response = requests.post(
            request_url,
            headers={
                "Authtoken": context.get_auth_token(),
                "Content-Type": content_type,
                "Accept": accept,
            },
            data=request_body,
        )

        if response.status_code == 200:
            response_data = ET.fromstring(response.text)
            record_id = response_data.findtext(".//id")

            context.log(
                f"Successfully updated record with id {record_id}",
            )
            return UpdateRecordResult(
                success=True,
                record_id=record_id,
                response_data=response_data,
            )

        context.log(
            f"❌ Failed to update record with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n",
            "error",
        )
        return UpdateRecordResult(
            success=False,
            error=f"Failed to update record with status {response.status_code}: {response.text}",
        )
    except requests.RequestException as e:
        context.log(
            f"❌ Request failed for update record with oldId {old_id_text}: {e}",
            "error",
        )
        return UpdateRecordResult(success=False, error=str(e))


def _parse_record(record: ET.Element):
    update_action_link = record.find("./actionLinks/update")
    assert update_action_link is not None, "Update action link not found in record"

    request_url = update_action_link.findtext("./url")
    assert request_url is not None, "Update URL not found in action link"
    content_type = update_action_link.findtext("./contentType")
    assert content_type is not None, "Content-Type not found in action link"
    accept = update_action_link.findtext("./accept")
    assert accept is not None, "Accept not found in action link"

    data = record.find("./data")
    assert data is not None, "Data element not found in record"
    data_group = data[0]
    assert data_group is not None, "Data group not found in data element"

    return [
        request_url,
        content_type,
        accept,
        data_group,
    ]
