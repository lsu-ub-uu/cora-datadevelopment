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
from multiprocessing import Pool
from tqdm import tqdm

context = None
with_binaries = False
apply = False


def main():
    """Main entry point for the outputs import script."""

    print_logo()

    args = _parse_args()
    outputs_import(
        xml_dir=args.xml_dir,
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        processes=args.processes,
        apply=args.apply,
        limit=args.limit,
        binaries=args.binaries,
        pids=args.pids.split(",") if args.pids else None,
    )


def outputs_import(
    xml_dir: str,
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
    apply: bool,
    limit: int | None = None,
    binaries: bool = False,
    pids: list[str] | None = None,
):
    start_time = time.perf_counter()

    source_records = _read_source_records(xml_dir, limit)

    if pids is not None:
        source_records = [
            record for record in source_records if record.findtext("pid") in pids
        ]

    # if not _validate_source_records(source_records):
    #     print("Source records validation failed. Exiting.")
    #     return
    print(f"Starting migration of {len(source_records)} records to {system} system...")
    counts = {"SUCCESS": 0, "CLASSIC_QUALITY": 0, "FAILED": 0, "DUPLICATE": 0}
    results = []
    with Pool(
        processes,
        _init_context,
        initargs=(
            system,
            login_id,
            app_token,
            apply,
            binaries,
        ),
    ) as pool, tqdm(total=len(source_records), desc="Migrating records") as progress:
        for result in pool.imap_unordered(_migrate_record, source_records):
            counts[result.status] += 1
            results.append(result)
            progress.set_postfix_str(
                f"✅ {counts['SUCCESS']} | ☣️ {counts['CLASSIC_QUALITY']} | ❌ {counts['FAILED']} | ⏭️ {counts['DUPLICATE']}"
            )
            progress.update(1)

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
            "--pids": {
                "help": "Comma-separated list of PIDs to process (for testing purposes)",
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
    assert context is not None, "Context must be initialized before migrating records"
    return output_migrate(source_record, context, apply, with_binaries=with_binaries)


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
    errors = {}
    for source_record in source_records:
        try:
            validate_xml(source_record, fedora_publication_xml_spec)
        except XMLValidationError as e:
            pid = source_record.findtext("pid")
            error_str = str(e)
            if error_str not in errors:
                errors[error_str] = []
            errors[error_str].append(pid)
    if len(errors) > 0:
        print("==== Skipped migration due to XML Validation Error in source data ==== ")
        for error in errors:
            print(f"❌ {error} - {len(errors[error])} occurrences")
            print(f"   Example pids: {', '.join(errors[error][:5])}...")
        return False
    return True


def _log_results(results: list[OutputMigrationResult]):
    main_script = os.path.basename(sys.argv[0])

    successful_migrations = []
    classic_quality_migrations = []
    failed_migrations = []
    skipped_migrations = []
    for result in results:
        error_str = ", ".join(result.errors) if result.errors else ""
        if result.status == "SUCCESS":
            successful_migrations.append(result.pid)
        elif result.status == "CLASSIC_QUALITY":
            classic_quality_migrations.append(f"{result.pid} - Errors: [{error_str}]")
        elif result.status == "DUPLICATE":
            skipped_migrations.append(
                f"{result.pid} - Skipped due to duplicate record with oldId alread in Cora"
            )
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
    logger.info(f"{len(skipped_migrations)} Records skipped due to duplicates:")
    for pid in skipped_migrations:
        logger.info(f"⏭️ {pid}")
    logger.info(f"{len(failed_migrations)} Records failed to import:")
    for error in failed_migrations:
        logger.info(f"❌ {error}")
    print(f"{len(successful_migrations)} succeeded, {len(failed_migrations)} failed.")


def _generate_report(results: list[OutputMigrationResult]):
    print("==== Migration Report ====")
    print(f"Total records processed: {len(results)}")
    status_counts = {"SUCCESS": 0, "CLASSIC_QUALITY": 0, "FAILED": 0, "DUPLICATE": 0}


if __name__ == "__main__":
    main()
