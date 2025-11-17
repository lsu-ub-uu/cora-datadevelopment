import requests
import xml.etree.ElementTree as ET
from typing import Literal, Tuple, List, Optional, TypeGuard
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
        desc=f"Creating {record_type} records in Cora {context.get_system()}",
    )

    successful_creates = [
        result for result in creation_results if is_success_result(result)
    ]
    creation_errors = [
        result for result in creation_results if not is_success_result(result)
    ]

    context.log(
        f"Created {len(record_list)} records. {len(successful_creates)} succeeded, {len(creation_errors)} failed."
    )

    return creation_results


class CreateRecordSuccessResult:
    def __init__(
        self,
        record_id: str,
        response_data: ET.Element,
    ):
        self.success = True
        self.record_id = record_id
        self.error = None
        self.response_data = response_data


class CreateRecordFailureResult:
    def __init__(
        self,
        error: str,
    ):
        self.success = False
        self.error = error
        self.record_id = None
        self.response_data = None


def create_record(
    record: ET.Element,
    *,
    record_type: str,
    context: Context,
) -> CreateRecordSuccessResult | CreateRecordFailureResult:
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
            assert record_id is not None, "Record ID not found in response"
            return CreateRecordSuccessResult(
                record_id=record_id, response_data=response_data
            )

        context.log(
            f"❌ Failed to create record for {record_type} with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n",
            "error",
        )
        return CreateRecordFailureResult(
            error=f"Failed to create record with status {response.status_code}: {response.text}",
        )
    except requests.RequestException as e:
        context.log(
            f"❌ Request failed for {record_type} with oldId {old_id_text}: {e}",
            "error",
        )
        return CreateRecordFailureResult(
            error=str(e),
        )


def is_success_result(
    result: CreateRecordSuccessResult | CreateRecordFailureResult,
) -> TypeGuard[CreateRecordSuccessResult]:
    return result.success
