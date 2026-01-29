import os
import sys
import time
from xml.etree import ElementTree as ET
from common.arg_parser import create_argument_parser
from common.run_rotating_logger import RunRotatingLogger
from cora.context import CoraContext
from scripts.util.analyze_errors import analyze_and_print_report
from fedora_to_cora.output_migrate import output_migrate, OutputMigrationResult
from common.xml_validate import validate_xml, XMLValidationError
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec
from common.common_data import read_source_xml
from common.print_logo import print_logo
from common.threads import run_with_multiprocessing

context = None
with_binaries = False
apply = False

def main():
    """Main entry point for the outputs import script."""
    
    print_logo()

    args = _parse_args()
    start_time = time.perf_counter()

    source_records = _read_source_records(args.xml_dir, args.limit)
    
    if not _validate_source_records(source_records):
        print("Source records validation failed. Exiting.")
        return
    
    results = run_with_multiprocessing(
        iterable=source_records,
        worker=_migrate_record,
        processes=args.processes,
        initializer=_init_context,
        initargs=(args.system, args.login_id, args.app_token, args.apply, args.binaries),
        desc="Processing source records",
    )

    _log_results(results)

    end_time = time.perf_counter()
    print(f"Processing completed in {end_time - start_time:.2f} seconds.")

    analyze_and_print_report("logs/outputs-import.log")

def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            "--xml-dir": {
                "help": "Directory containing XML files to process",
                "required": True,
            },
            "--system": {
                "default": "pre",
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--processes": {
                "type": int,
                "default": 2,
                "help": "Number of processes",
            },
            "--apply": {
                "action": "store_true",
                "help": "Create records in Cora. (If not set, will behave as a dry-run)",
            },
            "--limit": {
                "type": int,
                "help": "Limit the number of processed files (for testing purposes)",
                "default": None,
            },
            "--binaries": {
                "action": "store_true",
                "help": "Also migrate binaries associated with the publications",
                "default": False,
            },
        },
    )

    return parser.parse_args()

def _init_context(system, login_id, app_token, apply_flag, binaries_flag):
    global context, apply, with_binaries
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)
    apply = apply_flag
    with_binaries = binaries_flag

def _migrate_record(source_record):
    return output_migrate(
        source_record, context, apply, with_binaries=with_binaries
    )
   

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
        print(
            "==== Skipped migration due to XML Validation Error in source data ==== "
        )
        for error in validation_errors:
            print(f"❌ {error}")
        return False
    return True

def _log_results(results: list[OutputMigrationResult]):
    main_script = os.path.basename(sys.argv[0])

    successful_migrations = []
    classic_quality_migrations = []
    failed_migrations = []
    for result in results:
        error_str = ", ".join(result.errors) if result.errors else ""
        if result.status == "SUCCESS":
            successful_migrations.append(result.pid)
        elif result.status == "CLASSIC_QUALITY":
            classic_quality_migrations.append(f"{result.pid} - Errors: [{error_str}]")
        else:
            failed_migrations.append(f"{result.pid} - Errors: [{error_str}]")
            
    logger = RunRotatingLogger("data", f"logs/{main_script}.log").get()
    
    logger.info("==== Processing complete ====")

    logger.info(f"{len(successful_migrations)} Records successfully imported:")
    for pid in successful_migrations:
        logger.info(f"✅ {pid}")

    logger.info(
        f"{len(classic_quality_migrations)} Records imported with classic quality:"
    )
    for pid in classic_quality_migrations:
        logger.info(f"☣️ {pid}")

    logger.info(f"{len(failed_migrations)} Records failed to import:")
    for error in failed_migrations:
        logger.info(f"❌ {error}")
    print(f"{len(successful_migrations)} succeeded, {len(failed_migrations)} failed.")


if __name__ == "__main__":
    main()
