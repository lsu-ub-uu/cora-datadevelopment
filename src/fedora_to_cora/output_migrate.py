from typing import Tuple
import xml.etree.ElementTree as ET
from cora.context import Context
from cora.delete import delete_record
from fedora_to_cora.attachments_migrate import attachments_migrate
from fedora_to_cora.output_transform import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from cora.validate import validate_record
from cora.create import create_record, is_success_result


def output_migrate(
    source_record: ET.Element, context: Context, xml_dir: str, apply: bool = False
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

    if apply:
        create_record_result = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

        if is_success_result(create_record_result):
            success, errors = attachments_migrate(
                source_record,
                create_record_result.response_data,
                context,
                xml_dir,
            )
            if not success:
                context.log(
                    f"❌ Failed to migrate attachments for record with old id {source_record.findtext('.//pid')} Rolling back.",
                    level="error",
                )
                delete_record(create_record_result.response_data, context)
                return False, errors

        return create_record_result.success, (
            [create_record_result.error] if create_record_result.error else None
        )

    return True, None
