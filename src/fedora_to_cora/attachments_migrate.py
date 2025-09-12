from typing import Tuple
import xml.etree.ElementTree as ET
import os
import copy

import requests
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
    created_binary_records = []
    record_to_update = copy.deepcopy(cora_record)
    output = record_to_update.find("./data/output")
    assert output is not None, "Output element not found in created record"

    errors = []
    attachments = source_record.findall("./attachments/attachment")
    for attachment in attachments:
        attachment, error = _migrate_attachment(
            attachment, context, xml_dir, created_binary_records, source_record
        )
        if attachment is not None:
            output.append(attachment)
        if error is not None:
            errors.append(error)

    if not errors:
        update_record(record_to_update, context)
    else:
        # roll back all created binary records if there are errors
        for binary_record in created_binary_records:
            delete_record(binary_record, context)

    return len(errors) == 0, errors if errors else None


def _migrate_attachment(
    attachment: ET.Element,
    context: Context,
    xml_dir: str,
    created_binary_records: list[ET.Element],
    source_record: ET.Element,
) -> Tuple[ET.Element | None, str | None]:
    pid = source_record.findtext(".//pid")
    assert pid is not None, "PID not found in source record"
    binary_record = binary_record_transform(attachment)
    create_binary_result = create_record(
        binary_record,
        record_type="binary",
        context=context,
    )

    if is_success_result(create_binary_result):
        created_binary_records.append(create_binary_result.response_data)
        file_path = _get_file_path(pid, attachment, xml_dir)
        try:
            upload_binary(create_binary_result.response_data, file_path, context)
        except UploadError as e:
            context.log(f"Error uploading binary: {e}", level="error")
            return None, str(e)

        cora_attachment = attachment_transform(
            attachment,
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


def _get_file_path(pid: str, attachment: ET.Element, xml_dir: str) -> str:
    file_name = attachment.findtext("./fileName")
    file_suffix = attachment.findtext("./mimeType/fileSuffix")
    file_path = f"{xml_dir}/binaries/{pid}/{file_name}.{file_suffix}"
    return file_path
