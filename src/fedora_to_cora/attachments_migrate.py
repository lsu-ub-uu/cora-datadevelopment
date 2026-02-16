from typing import Tuple
import xml.etree.ElementTree as ET
import copy

from cora.context import Context
from fedora_to_cora.binary_migrate import migrate_binary
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)
from fedora_to_cora.transform.binary.binary_record_transform import (
    binary_record_transform,
)
from cora.create import create_record, is_success_result
from cora.update import update_record
from cora.delete import delete_record
from fedora_to_cora.transform.attachment_transform import attachment_transform
from common.xml_utils import append_if_value


def attachments_migrate(
    source_record: ET.Element,
    cora_record: ET.Element,
    context: Context,
) -> Tuple[bool, list[str] | None]:
    created_binary_records = []
    record_to_update = copy.deepcopy(cora_record)
    output = record_to_update.find("./data/output")
    assert output is not None, "Output element not found in created record"

    errors = []
    attachments = source_record.findall("./attachments/attachment")
    if len(attachments) > 0:
        attachments_group = ET.SubElement(output, "attachments")
        append_if_value(attachments_group, _create_reviewed(source_record))
        append_if_value(attachments_group, _create_note(source_record))
        for attachment in _sort_by_order(attachments):
            if attachment.findtext("./deleted") == "true":
                context.log(
                    f"🗑️ Skipping deleted attachment {attachment.findtext('./fileName')} for record with old id {source_record.findtext('.//pid')}"
                )
                continue

            attachment, error = _migrate_attachment(
                attachment, context, created_binary_records, source_record
            )
            if attachment is not None:
                attachments_group.append(attachment)
            if error is not None:
                errors.append(error)

        if not errors and len(attachments_group.findall("./attachment")) > 0:
            update_result = update_record(record_to_update, context)
            if update_result.success:
                context.log(
                    f"✅ Successfully migrated {len(attachments_group.findall('./attachment'))} attachments for record with old id {source_record.findtext('.//pid')}"
                )
            else:
                context.log(
                    f"❌ Failed to update record with attachments for record with old id {source_record.findtext('.//pid')}: {update_result.error}",
                    level="error",
                )
                errors.append(update_result.error)
                _roll_back_binary_records(created_binary_records, context)
        else:
            context.log(
                "❌ Errors occurred during attachment migration, rolling back created binary records.",
                level="error",
            )
            _roll_back_binary_records(created_binary_records, context)

    success = len(errors) == 0
    errors = errors if errors else None

    return success, errors


def _roll_back_binary_records(
    created_binary_records: list[ET.Element], context: Context
):
    for binary_record in created_binary_records:
        delete_record(binary_record, context)


def _migrate_attachment(
    attachment: ET.Element,
    context: Context,
    created_binary_records: list[ET.Element],
    source_record: ET.Element,
) -> Tuple[ET.Element | None, str | None]:
    pid = source_record.findtext("./pid")
    file_name = attachment.findtext("./fileName")
    assert pid is not None and file_name is not None

    binary_record = binary_record_transform(attachment)
    create_binary_result = create_record(
        binary_record,
        record_type="binary",
        context=context,
    )

    if is_success_result(create_binary_result):
        created_binary_records.append(create_binary_result.response_data)
        try:
            migrate_binary(
                create_binary_result.response_data,
                pid=pid,
                file_name=file_name,
                context=context,
            )
        except Exception as e:
            context.log(f"🥵 [PID {pid}] Error migrating binary: {e}", level="error")
            return None, str(e)

        validation_type = get_validation_type_from_fedora_record(source_record)
        assert validation_type is not None

        cora_attachment = attachment_transform(
            attachment,
            validation_type=validation_type,
            binary_record_id=create_binary_result.record_id,
            file_upload_message=source_record.findtext(
                "./administrativeInfo/fileUploadMessage"
            ),
        )
        return cora_attachment, None
    else:
        context.log(
            f"❌ Failed to create binary record for attachment {attachment.findtext('./name')}: {create_binary_result.error}",
            "error",
        )
        return None, create_binary_result.error


def _sort_by_order(attachments: list[ET.Element]) -> list[ET.Element]:
    return sorted(
        attachments, key=lambda attachment: attachment.findtext("./order") or ""
    )


def _create_note(source_record: ET.Element) -> ET.Element | None:
    file_upload_message = source_record.findtext(
        "./administrativeInfo/fileUploadMessage"
    )
    if file_upload_message is not None and file_upload_message.strip() != "":
        note = ET.Element("note")
        note.text = file_upload_message
        return note


def _create_reviewed(source_record: ET.Element) -> ET.Element | None:
    attachments = source_record.findall("./attachments/attachment")

    reviewed = ET.Element("reviewed")
    if any(_is_attachment_waiting_for_review(attachment) for attachment in attachments):
        reviewed.text = "false"
    else:
        reviewed.text = "true"

    return reviewed


def _is_attachment_waiting_for_review(attachment: ET.Element) -> bool:
    to_be_published = attachment.findtext("./toBePublished")
    to_be_archived = attachment.findtext("./toBeArchived")
    temp_available_from = attachment.findtext("./tempAvailableFrom")

    return (
        to_be_published == "true"
        or to_be_archived == "true"
        or temp_available_from is not None
    )
