import xml.etree.ElementTree as ET
from cora.context import Context
from fedora_to_cora.output_transform import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from cora.validate import validate_record
from cora.create import create_record


def output_migrate(source_record: ET.Element, context: Context, dry_run: bool = True):
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

    if not dry_run:
        valid, errors = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )
        # TODO Handle binaries

    return valid, errors
