import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from typing import Literal
from common.xml_utils import pretty_print_xml
from common.xml_utils import create_group, create_text

from cora_python_client import CoraClient, CoraConflictError, CoraRecord, CoraError

logger = logging.getLogger(__name__)


@dataclass
class MigrateOldRecordResult:
    status: Literal["CREATED", "SKIPPED", "FAILED"]
    cora_old_record_id: str | None
    error: str | None


def old_record_migrate(
    source_record: ET.Element,
    cora_client: CoraClient,
) -> MigrateOldRecordResult:
    old_id = source_record.findtext("./pid")

    # Transform to old record record
    old_record_data = _transform_old_record(source_record)

    # Create old record record
    try:
        old_record = cora_client.create_record(
            old_record_data, record_type="diva-oldRecord"
        )
        logger.info(
            "Created old record with oldId %s and ID: %s",
            old_id,
            old_record.id,
        )
    except CoraError as error:
        logger.error(f"Failed to create old record for oldId {old_id}: %s", error)
        return _handle_failed_to_create_old_record(error, source_record)

    try:
        binary_record = _create_and_upload_binary(
            old_record.id, source_record, cora_client
        )
        logger.info(
            "Created binary record with oldId %s and ID: %s",
            old_id,
            binary_record.id,
        )
    except CoraError as error:
        logger.error(
            f"Failed to create and upload binary for old record with oldId {old_id}: %s",
            error,
        )
        return _create_failure_result("Failed to create and upload binary", error)

    # Update old record record with link to binary record
    try:
        _update_old_record_with_binary_link(
            old_record,
            binary_record.id,
            cora_client,
        )
        logger.info(
            "Updated old record with binary link successfully for oldId %s", old_id
        )
    except CoraError as error:
        logger.error(
            f"Failed to update old record with binary link for oldId {old_id}: %s",
            error,
        )
        return _create_failure_result(
            "Failed to update oldRecord with binary link", error
        )

    return MigrateOldRecordResult(
        "CREATED",
        old_record.id,
        None,
    )


def _create_failure_result(
    message: str, exception: Exception
) -> MigrateOldRecordResult:
    return MigrateOldRecordResult(
        "FAILED",
        None,
        f"{message}: {exception}",
    )


def _handle_failed_to_create_old_record(
    error: CoraError, source_record: ET.Element
) -> MigrateOldRecordResult:
    if _is_duplicate_error(error, source_record):
        return MigrateOldRecordResult(
            "SKIPPED", None, "Cora diva-oldRecord record already exists"
        )
    return _create_failure_result("Failed to create diva-oldRecord", error)


def _is_duplicate_error(error: CoraError, source_record: ET.Element) -> bool:
    if not isinstance(error, CoraConflictError):
        return False
    old_id = source_record.findtext("./pid")
    duplicate_error = f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
    return duplicate_error in error.message


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


def _create_and_upload_binary(
    binary_record_id: str,
    source_record: ET.Element,
    cora_client: CoraClient,
):
    return cora_client.create_and_upload_binary(
        visibility="published",
        host_record_type="diva-oldRecord",
        host_record_id=binary_record_id,
        original_file_name=f"{source_record.findtext('./pid')}.xml",
        data=pretty_print_xml(source_record, xml_declaration=True).encode("utf-8"),
    )


def _update_old_record_with_binary_link(
    old_record: CoraRecord, binary_record_id: str, cora_client: CoraClient
):
    binary_link_group = create_group(
        "record",
        repeatId="0",
        children=[
            create_text("linkedRecordType", value="binary"),
            create_text("linkedRecordId", value=binary_record_id),
        ],
    )
    assert binary_link_group is not None
    old_record.data_group.append(binary_link_group)
    return cora_client.update_record(old_record)
