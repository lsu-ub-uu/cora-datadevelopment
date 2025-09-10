from common.common_data import read_source_xml
import os
from common.threads import run_with_threads
from cora.context import CoraContext, Context
from fedora_to_cora.output_migrate import output_migrate
from common.xml_validate import validate_xml, XMLValidationError
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec
import xml.etree.ElementTree as ET


def process_fedora_publication_files(
    xml_dir: str, context: Context, apply: bool = False
):
    context.log("==== Begin processing Fedora XML publications ====")
    context.log(
        f"==== xml_dir={xml_dir}, system={context.get_system()}, apply={apply} ===="
    )
    context.log("=" * 50)

    source_records = _read_source_records(xml_dir)

    source_records_valid = _validate_source_records(source_records, context)

    if source_records_valid:
        _migrate_records(source_records, context, xml_dir, apply)

    print(f"Output logged to {context.get_logger().handlers[0].baseFilename}")  # type: ignore[attr-defined]


def _read_source_records(xml_dir):
    return [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]


def _validate_source_records(source_records, context: Context) -> bool:
    validation_errors = []
    for source_record in source_records:
        try:
            validate_xml(source_record, fedora_publication_xml_spec)
        except XMLValidationError as e:
            pid = source_record.findtext("pid")
            validation_errors.append(f"{pid} - XML Validation Error: {str(e)}")
    if len(validation_errors) > 0:
        context.log(
            "==== Skipped migration due to XML Validation Error in source data ==== "
        )
        for error in validation_errors:
            context.log(f"❌ {error}")
        return False
    return True


def _migrate_records(
    source_records: list[ET.Element], context: Context, xml_dir: str, apply: bool
):
    successful_transformations = []
    failed_transformations = []

    def process_file(source_record):
        pid = source_record.findtext("pid")
        context.log(f"--- Processing record with pid: {pid} ---")
        try:
            valid, errors = output_migrate(source_record, context, xml_dir, apply)
            if valid:
                successful_transformations.append(pid)
            else:
                failed_transformations.append(
                    f"{pid} - Errors: [{', '.join(errors) if errors else ''}]"
                )
        except Exception as e:
            failed_transformations.append(f"{pid} - Exception: {str(e)}")

    run_with_threads(
        source_records,
        process_file,
        workers=8,
        desc="Processing publication files",
    )

    context.log("==== Processing complete ====")

    context.log(f"{len(successful_transformations)} Successful transformations:")
    for pid in successful_transformations:
        context.log(f"✅ {pid}")

    context.log(f"{len(failed_transformations)} Failed transformations:")
    for error in failed_transformations:
        context.log(f"❌ {error}")
    print(
        f"{len(successful_transformations)} succeeded, {len(failed_transformations)} failed."
    )
