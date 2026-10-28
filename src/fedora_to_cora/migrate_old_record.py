import hashlib
import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from typing import Literal
from common.common_data import create_record_link
from common.create_binary_record_data import create_binary_record_data
from common.xml_utils import pretty_print_xml
from common.xml_utils import create_group, create_text
from cora.create import (
    create_record,
    is_success_result,
    CreateRecordSuccessResult,
    CreateRecordFailureResult,
)
from cora.context import Context
from cora.upload import UploadError, upload_binary
from cora.update import update_record

logger = logging.getLogger(__name__)


@dataclass
class MigrateOldRecordResult:
    status: Literal["CREATED", "SKIPPED", "FAILED"]
    cora_old_record_id: str | None
    error: str | None


def old_record_migrate(
    source_record: ET.Element,
    context: Context,
) -> MigrateOldRecordResult:
    old_id = source_record.findtext("./pid")

    # Transform to old record record
    old_record = _transform_old_record(source_record)

    # Create old record record
    create_old_record_result = create_record(
        old_record, record_type="diva-oldRecord", context=context
    )
    if not is_success_result(create_old_record_result):
        logger.error(
            f"Failed to create old record for oldId {old_id}: %s",
            create_old_record_result.error,
        )
        return _handle_failed_to_create_old_record(
            create_old_record_result, source_record
        )
    logger.info(
        "Created old record with oldId %s and ID: %s",
        old_id,
        create_old_record_result.record_id,
    )

    binary_data = pretty_print_xml(source_record, xml_declaration=True).encode("utf-8")
    create_binary_record_result = _create_binary_record(
        create_old_record_result.record_id, source_record, binary_data, context
    )
    if not is_success_result(create_binary_record_result):
        logger.error(
            f"Failed to create binary for old record with oldId {old_id}: %s",
            create_binary_record_result.error,
        )
        return _create_failure_result(
            f"Failed to create binary for oldRecord: {create_binary_record_result.error}"
        )
    logger.info(
        "Created binary record with oldId %s and ID: %s",
        old_id,
        create_binary_record_result.record_id,
    )

    # Upload binary file
    try:
        _upload_binary_data(
            create_binary_record_result.response_data,
            source_record,
            binary_data,
            context,
        )
        logger.info("Uploaded binary for old record with oldId %s successfully", old_id)
    except UploadError as e:
        logger.error(
            "Failed to upload binary for old record with oldId %s: %s", old_id, e
        )
        return _create_failure_result(f"Failed to upload binary for oldRecord: {e}")

    # Update old record record with link to binary record
    update_record_result = _update_old_record_with_binary_link(
        create_old_record_result.response_data,
        create_binary_record_result.record_id,
        context,
    )
    if not update_record_result.success:
        logger.error(
            "Failed to update old record with binary link for oldId %s: %s",
            old_id,
            update_record_result.error,
        )
        return _create_failure_result(
            f"Failed to update oldRecord with binary link: {update_record_result.error}"
        )

    logger.info("Updated old record with binary link successfully for oldId %s", old_id)
    return MigrateOldRecordResult(
        "CREATED",
        create_old_record_result.record_id,
        None,
    )


def _create_failure_result(error: str) -> MigrateOldRecordResult:
    return MigrateOldRecordResult(
        "FAILED",
        None,
        error,
    )


def _handle_failed_to_create_old_record(
    create_old_record_result, source_record: ET.Element
) -> MigrateOldRecordResult:
    if _is_duplicate_error(create_old_record_result.error, source_record):
        return MigrateOldRecordResult(
            "SKIPPED", None, "Cora diva-oldRecord record already exists"
        )
    return _create_failure_result(
        f"Failed to create diva-oldRecord: {create_old_record_result.error}"
    )


def _is_duplicate_error(error: str | None, source_record: ET.Element) -> bool:
    if error is None:
        return False
    old_id = source_record.findtext("./pid")
    duplicate_error = f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
    return duplicate_error in error


def _transform_old_record(source_record: ET.Element) -> ET.Element:
    old_record = create_group(
        "oldRecord",
        children=[
            create_group(
                "recordInfo",
                children=[
                    create_group(
                        "validationType",
                        children=[
                            create_text("linkedRecordType", value="validationType"),
                            create_text("linkedRecordId", value="diva-oldRecord"),
                        ],
                    ),
                    create_group(
                        "dataDivider",
                        children=[
                            create_text("linkedRecordType", value="system"),
                            create_text("linkedRecordId", value="divaData"),
                        ],
                    ),
                    create_text("oldId", value=source_record.findtext("./pid")),
                ],
            )
        ],
    )
    assert old_record is not None
    return old_record


def _create_binary_record(
    binary_record_id: str,
    source_record: ET.Element,
    binary_data: bytes,
    context,
) -> CreateRecordSuccessResult | CreateRecordFailureResult:
    binary_record = create_binary_record_data(
        visibility="published",
        host_record_type="diva-oldRecord",
        host_record_id=binary_record_id,
        original_file_name=f"{source_record.findtext('./pid')}.xml",
        expected_checksum=hashlib.sha512(binary_data).hexdigest(),
        expected_file_size=str(len(binary_data)),
    )
    return create_record(binary_record, record_type="binary", context=context)


def _upload_binary_data(
    created_binary_record: ET.Element,
    source_record: ET.Element,
    binary_data: bytes,
    context: Context,
):
    upload_binary(
        created_binary_record,
        f"{source_record.findtext('./pid')}.xml",
        binary_data,
        context=context,
    )


def _update_old_record_with_binary_link(
    old_record_record: ET.Element, binary_record_id: str, context: Context
):
    old_record_group = old_record_record.find("./data/oldRecord")
    assert old_record_group is not None, "Old record group not found in response"
    binary_link_group = create_group(
        "record",
        repeatId="0",
        children=[
            create_text("linkedRecordType", value="binary"),
            create_text("linkedRecordId", value=binary_record_id),
        ],
    )
    assert binary_link_group is not None
    old_record_group.append(binary_link_group)

    return update_record(old_record_record, context=context)
