from common.common_data import read_source_xml
import os
from common.threads import run_with_multiprocessing
from cora.context import Context
from fedora_to_cora.output_migrate import output_migrate
from common.xml_validate import validate_xml, XMLValidationError
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec
import xml.etree.ElementTree as ET


def process_fedora_publication_files(
    xml_dir: str,
    context: Context,
    apply: bool = False,
    limit: int | None = None,
    binaries: bool = False,
):
    context.log("==== Begin processing Fedora XML publications ====")
    context.log(
        f"==== xml_dir={xml_dir}, system={context.get_system()}, apply={apply} limit={limit} ===="
    )
    context.log("=" * 50)

    source_records = _read_source_records(xml_dir, limit)

    source_records_valid = _validate_source_records(source_records, context)

    if source_records_valid:
        _migrate_records(source_records, context, apply, with_binaries=binaries)

    print(f"Output logged to {context.get_logger().handlers[0].baseFilename}")  # type: ignore[attr-defined]


def _read_source_records(xml_dir: str, limit: int | None = None) -> list[ET.Element]:
    records = [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]
    if limit is not None:
        return records[:limit]
    return records


def _validate_source_records(source_records) -> bool:
    validation_errors = []
    for source_record in source_records:
        try:
            validate_xml(source_record, fedora_publication_xml_spec)
        except XMLValidationError as e:
            pid = source_record.findtext("pid")
            validation_errors.append(f"{pid} - XML Validation Error: {str(e)}")
    if len(validation_errors) > 0:
        # context.log(
        #     "==== Skipped migration due to XML Validation Error in source data ==== "
        # )
        # for error in validation_errors:
        #     context.log(f"❌ {error}")
        return False
    return True


def _migrate_records(
    source_records: list[ET.Element], context: Context, apply: bool, with_binaries: bool
):
    successful_migrations = []
    classic_quality_migrations = []
    failed_migrations = []

    def process_file(source_record):
        pid = source_record.findtext("pid")
        context.log(f"--- Processing record with pid: {pid} ---")
        try:
            result = output_migrate(
                source_record, context, apply, with_binaries=with_binaries
            )
            error_str = ", ".join(result.errors) if result.errors else ""
            if result.status == "SUCCESS":
                successful_migrations.append(pid)
            elif result.status == "CLASSIC_QUALITY":
                classic_quality_migrations.append(f"{pid} - Errors: [{error_str}]")
            else:
                failed_migrations.append(f"{pid} - Errors: [{error_str}]")
        except Exception as e:
            failed_migrations.append(f"{pid} - Exception: {str(e)}")
    
   


    # run_with_threads(
    #     source_records,
    #     process_file,
    #     workers=context.get_workers(),
    #     desc="Processing publication files",
    # )

    context.log("==== Processing complete ====")

    context.log(f"{len(successful_migrations)} Records successfully imported:")
    for pid in successful_migrations:
        context.log(f"✅ {pid}")

    context.log(
        f"{len(classic_quality_migrations)} Records imported with classic quality:"
    )
    for pid in classic_quality_migrations:
        context.log(f"☣️ {pid}")

    context.log(f"{len(failed_migrations)} Records failed to import:")
    for error in failed_migrations:
        context.log(f"❌ {error}")
    print(f"{len(successful_migrations)} succeeded, {len(failed_migrations)} failed.")
