import requests
import xml.etree.ElementTree as ET
from typing import Tuple, List, Optional
from cora.context import Context
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml


def create_record_list(
    record_list: list[ET.Element], record_type: str, context: Context
):
    creation_results = run_with_threads(
        record_list,
        lambda record: create_record(record, record_type=record_type, context=context),
        workers=context.get_workers(),
        desc="Creating records",
    )

    successful_creates = [valid for (valid, _) in creation_results if valid]
    creation_errors = [errors for (valid, errors) in creation_results if not valid]

    context.log(
        f"Created {len(record_list)} records. {len(successful_creates)} succeeded, {len(creation_errors)} failed."
    )

    return creation_results


class CreateRecordResult:
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


def create_record(
    record: ET.Element,
    *,
    record_type: str,
    context: Context,
) -> CreateRecordResult:
    """Creates a Cora record from the given XML element.

    :param record: The XML element representing the record to create.
    :param record_type: The type of the record to create (e.g., "diva-output").
    :param context: The Cora context containing authentication and configuration information.

    :return: A CreateRecordResult object containing the success status, record ID (if successful), and any error messages.
    """

    old_id = record.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    request_body = (
        f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(record).decode("UTF-8")}'
    )

    try:
        response = requests.post(
            f"{context.get_base_url()}{record_type}",
            headers={
                "Authtoken": context.get_auth_token(),
                "Content-Type": "application/vnd.cora.recordgroup+xml",
                "Accept": "application/vnd.cora.record+xml",
            },
            data=request_body,
        )

        if response.status_code == 201:
            response_data = ET.fromstring(response.text)
            record_id = response_data.findtext(".//recordInfo/id")
            print(pretty_print_xml(response_data))
            assert record_id is not None, "Record ID not found in response"
            return CreateRecordResult(
                success=True, record_id=record_id, response_data=response_data
            )

        context.log(
            f"❌ Failed to create record for {record_type} with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n",
            "error",
        )
        return CreateRecordResult(
            success=False,
            error=f"Failed to create record with status {response.status_code}: {response.text}",
        )
    except requests.RequestException as e:
        context.log(
            f"❌ Request failed for {record_type} with oldId {old_id_text}: {e}",
            "error",
        )
        return CreateRecordResult(success=False, error=str(e))
