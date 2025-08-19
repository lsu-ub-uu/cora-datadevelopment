import os
from typing import Tuple
import xml.etree.ElementTree as ET
from cora.context import Context
from cora.update import update_record
from cora.upload import upload_binary
from fedora_to_cora.output_transform import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from cora.validate import validate_record
from cora.create import create_record
from fedora_to_cora.transform.binary.create_binary_record import create_binary_record
from common.common_data import create_record_link_using_name_type_id


def output_migrate(
    source_record: ET.Element, context: Context, xml_dir: str, dry_run: bool = True
) -> Tuple[bool, list[str] | None]:
    """
    Migrates a Fedora XML publication record and its attached binaries to Cora.
    """

    cora_output = transform_to_cora_output(source_record, context)

    context.log(pretty_print_xml(cora_output))

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )

    if not valid:
        return False, errors

    if not dry_run:
        result = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

        created_record = result.response_data

        if result.success and result.record_id and created_record:
            binary_record_ids: list[str] = []
            record_id = result.record_id

            attachments = source_record.findall("./attachments/attachment")
            for attachment in attachments:
                binary_record = create_binary_record(attachment)
                create_binary_result = create_record(
                    binary_record,
                    record_type="binary",
                    context=context,
                )
                if (
                    create_binary_result.response_data
                    and create_binary_result.record_id
                ):
                    binary_record_ids.append(create_binary_result.record_id)
                    path = attachment.findtext("./path")
                    assert path is not None, "Path not found in attachment"
                    file_path = os.path.join(xml_dir, "binaries", path)

                    upload_binary(
                        create_binary_result.response_data, file_path, context
                    )

                if create_binary_result.error:
                    print(
                        f"Error creating binary record for attachment {attachment.findtext('./path')}: {create_binary_result.error}"
                    )

            if len(binary_record_ids) > 0:
                output = created_record.find("./data/output")
                assert output is not None, "Output element not found in response data"
                repeat_id = 0
                for repeat_id, binary_record_id in enumerate(binary_record_ids):
                    attachment = ET.SubElement(
                        output, "attachment", repeatId=str(repeat_id)
                    )
                    attachment.append(
                        create_record_link_using_name_type_id(
                            name_in_data="attachmentFile",
                            record_type="binary",
                            record_id=binary_record_id,
                        )
                    )
                    ET.SubElement(attachment, "type").text = "fullText"

                    admin_info = ET.SubElement(attachment, "adminInfo")
                    ET.SubElement(admin_info, "availability").text = "availableNow"

                update_record(
                    record=created_record,
                    context=context,
                )

            # upload binary to binary post

        return result.success, [result.error] if result.error else None

    return True, None
