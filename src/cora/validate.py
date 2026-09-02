import requests
import xml.etree.ElementTree as ET
from typing import Tuple, List, Optional
from common.xml_utils import create_group, create_text, pretty_print_xml
from cora.context import Context
from common.threads import run_with_threads


def validate_record_list(
    record_list: list[ET.Element], record_type: str, context: Context
):
    validation_results: List[Tuple[bool, Optional[List[str]]]] = run_with_threads(
        record_list,
        lambda record: validate_record(
            record, record_type=record_type, context=context
        ),
        workers=context.get_workers(),
        desc="Validating records",
    )

    valid_records = [valid for (valid, _) in validation_results if valid]
    validation_errors = [errors for (valid, errors) in validation_results if not valid]

    context.log(
        f"Validated {len(record_list)} records. {len(valid_records)} valid, {len(validation_errors)} invalid."
    )

    return validation_results


def validate_record(
    record: ET.Element, *, record_type: str, context: Context
) -> Tuple[bool, Optional[List[str]]]:
    validate_url = context.get_base_url() + "workOrder"
    headers = {
        "Content-Type": "application/vnd.cora.workorder+xml",
        "Accept": "application/vnd.cora.record+xml",
        "authToken": context.get_auth_token(),
    }

    old_id = record.find(".//oldId")
    old_id_text = old_id.text if old_id is not None else "N/A"

    validation_order = _create_validation_order(record_type, record)

    request_body = f'<?xml version="1.0" encoding="UTF-8"?>{ET.tostring(validation_order).decode("UTF-8")}'

    try:
        response = requests.post(validate_url, data=request_body, headers=headers)

        if response.status_code != 200 or not response.text:
            context.log(
                f"⚠️ Failed to validate {record_type} with oldId {old_id_text}: {response.status_code}.\nRecord XML: \n{pretty_print_xml(record)}",
                "error",
            )
            return (False, [f"Validation failed with status {response.status_code}"])

        response_data = ET.fromstring(response.text)
        valid = response_data.find(".//valid")

        if valid is not None and valid.text == "true":
            return (True, None)

        errors = [
            msg.text for msg in response_data.findall(".//errorMessage") if msg.text
        ]
        context.log(
            f"❌ Validation failed for {record_type} with oldId {old_id_text}.\n\nErrors:\n - {"\n - ".join(errors)}\n\nRecord XML: \n{pretty_print_xml(record)}",
            "error",
        )
        return (False, errors)
    except requests.RequestException as e:
        context.log(
            f"❌ Request failed for {record_type} with oldId {old_id_text}: {e}",
            "error",
        )
        return (False, [str(e)])


def _create_validation_order(record_type: str, record: ET.Element) -> ET.Element:
    record_element = ET.Element("record")
    record_element.append(record)
    work_order = create_group(
        "workOrder",
        [
            create_group(
                "order",
                [
                    create_group(
                        "validationOrder",
                        [
                            create_group(
                                "recordInfo",
                                [
                                    create_group(
                                        "dataDivider",
                                        [
                                            create_text("linkedRecordType", "system"),
                                            create_text("linkedRecordId", "divaData"),
                                        ],
                                    ),
                                    create_group(
                                        "validationType",
                                        [
                                            create_text(
                                                "linkedRecordType", "validationType"
                                            ),
                                            create_text(
                                                "linkedRecordId", "validationOrder"
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            create_group(
                                "recordType",
                                [
                                    create_text("linkedRecordType", "recordType"),
                                    create_text("linkedRecordId", record_type),
                                ],
                            ),
                            create_text("validateLinks", "false"),
                            create_text("metadataToValidate", "new"),
                        ],
                    )
                ],
            ),
            record_element,
        ],
    )
    assert work_order is not None
    return work_order
