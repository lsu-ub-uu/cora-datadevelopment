from typing import Tuple
import xml.etree.ElementTree as ET
import copy

from classic.download_attachment import download_attachment
from cora.context import Context
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)
from fedora_to_cora.transform.binary.binary_record_transform import (
    binary_record_transform,
)
from cora.create import create_record, is_success_result
from cora.update import update_record
from cora.upload import UploadError, upload_binary
from cora.delete import delete_record
from fedora_to_cora.transform.attachment_transform import attachment_transform


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
    for attachment in _sort_by_order(attachments):
        attachment, error = _migrate_attachment(
            attachment, context, created_binary_records, source_record
        )
        if attachment is not None:
            output.append(attachment)
        if error is not None:
            errors.append(error)

    if not errors:
        update_result = update_record(record_to_update, context)
        if update_result.success:
            context.log(
                f"✅ Successfully migrated {len(attachments)} attachments for record with old id {source_record.findtext('.//pid')}"
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

    return len(errors) == 0, errors if errors else None


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
            binary_data = download_attachment(pid, file_name)
        except Exception as e:
            context.log(
                f"Error downloading file for pid '{pid}' with filename '{file_name}': {e}",
                level="error",
            )
            return None, str(e)

        try:
            upload_binary(
                create_binary_result.response_data,
                file_name=file_name,
                data=binary_data,
                context=context,
            )
        except UploadError as e:
            context.log(f"Error uploading binary: {e}", level="error")
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
