from typing import Tuple
import xml.etree.ElementTree as ET
import os
import copy
from cora.context import Context
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
    xml_dir: str,
) -> Tuple[bool, list[str] | None]:
    record_to_update = copy.deepcopy(cora_record)
    output = record_to_update.find("./data/output")
    assert output is not None, "Output element not found in created record"

    errors = []
    attachments = source_record.findall("./attachments/attachment")
    for attachment in attachments:
        attachment, error = _migrate_attachment(attachment, context, xml_dir)
        if attachment is not None:
            output.append(attachment)
        if error is not None:
            errors.append(error)

    if not errors:
        update_record(record_to_update, context)

    return len(errors) == 0, errors if errors else None


def _migrate_attachment(
    attachment: ET.Element, context: Context, xml_dir: str
) -> Tuple[ET.Element | None, str | None]:
    binary_record = binary_record_transform(attachment)
    create_binary_result = create_record(
        binary_record,
        record_type="binary",
        context=context,
    )

    if is_success_result(create_binary_result):
        file_path = _get_file_path(attachment, xml_dir)
        try:
            upload_binary(create_binary_result.response_data, file_path, context)
        except UploadError as e:
            context.log(f"Error uploading binary: {e}", level="error")
            return None, str(e)

        cora_attachment = attachment_transform(
            attachment,
            binary_record_id=create_binary_result.record_id,
        )
        return cora_attachment, None
    else:
        context.log(
            f"❌ Failed to create binary record for attachment {attachment.findtext('./name')}: {create_binary_result.error}",
            "error",
        )
        return None, create_binary_result.error


def _get_file_path(attachment: ET.Element, xml_dir: str) -> str:
    path = attachment.findtext("./path")
    assert path is not None, "Path not found in attachment"
    return os.path.join(xml_dir, "binaries", path)
