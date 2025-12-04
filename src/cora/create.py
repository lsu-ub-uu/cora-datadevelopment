import requests
import xml.etree.ElementTree as ET
import time
from typing import Literal, Tuple, List, Optional, TypeGuard
from cora.context import Context
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml


def create_record_list(
    record_list: list[ET.Element],
    record_type: str,
    context: Context,
    max_retries: int = 3,
    initial_delay: float = 1.0,
):
    creation_results = run_with_threads(
        record_list,
        lambda record: create_record(
            record,
            record_type=record_type,
            context=context,
            max_retries=max_retries,
            initial_delay=initial_delay,
        ),
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
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> CreateRecordSuccessResult | CreateRecordFailureResult:
    """Creates a Cora record from the given XML element.

    :param record: The XML element representing the record to create.
    :param record_type: The type of the record to create (e.g., "diva-output").
    :param context: The Cora context containing authentication and configuration information.
    :param max_retries: Maximum number of retries for 409 Conflict responses (default: 3).
    :param initial_delay: Initial delay in seconds before retry, doubles with each retry (default: 1.0).

    :return: A CreateRecordResult object containing the success status, record ID (if successful), and any error messages.
    """

    old_id = record.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    request_body = (
        f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(record).decode("UTF-8")}'
    )

    for attempt in range(max_retries + 1):
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
                if attempt > 0:
                    context.log(
                        f"✅ Successfully created record for {record_type} with oldId {old_id_text} on attempt {attempt + 1}",
                        "info",
                    )
                return CreateRecordSuccessResult(
                    record_id=record_id, response_data=response_data
                )

            if response.status_code == 409 and attempt < max_retries:
                delay = initial_delay * (2**attempt)
                context.log(
                    f"⚠️ Conflict (409) for {record_type} with oldId {old_id_text}. Retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1})",
                    "warning",
                )
                time.sleep(delay)
                continue

            context.log(
                f"❌ Failed to create record for {record_type} with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n",
                "error",
            )
            return CreateRecordFailureResult(
                error=f"Failed to create record with status {response.status_code}: {response.text}",
            )
        except requests.RequestException as e:
            if attempt < max_retries:
                delay = initial_delay * (2**attempt)
                context.log(
                    f"⚠️ Request exception for {record_type} with oldId {old_id_text}: {e}. Retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1})",
                    "warning",
                )
                time.sleep(delay)
                continue
            else:
                context.log(
                    f"❌ Request failed for {record_type} with oldId {old_id_text}: {e}",
                    "error",
                )
                return CreateRecordFailureResult(
                    error=str(e),
                )

    return CreateRecordFailureResult(
        error="Maximum retries exceeded",
    )


def is_success_result(
    result: CreateRecordSuccessResult | CreateRecordFailureResult,
) -> TypeGuard[CreateRecordSuccessResult]:
    return result.success
