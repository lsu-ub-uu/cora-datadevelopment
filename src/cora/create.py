import requests
import xml.etree.ElementTree as ET
from typing import Tuple, List, Optional
from cora.context import Context
from common.threads import run_with_threads


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


def create_record(
    record: ET.Element,
    *,
    record_type: str,
    context: Context,
) -> Tuple[bool, Optional[List[str]]]:

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
            return True, None

        context.log(
            f"❌ Failed to create record for {record_type} with oldId {old_id_text}. \n\nStatus: {response.status_code}\n{response.text}\n",
            "error",
        )
        return False, [
            f"Failed to create record with status {response.status_code}: {response.text}"
        ]
    except requests.RequestException as e:
        context.log(
            f"❌ Request failed for {record_type} with oldId {old_id_text}: {e}",
            "error",
        )
        return False, [str(e)]
