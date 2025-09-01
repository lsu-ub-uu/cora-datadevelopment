from common.common_data import read_source_xml
import os
from common.threads import run_with_threads
from cora.context import CoraContext, Context
from fedora_to_cora.output_migrate import output_migrate


def process_fedora_publication_files(
    xml_dir: str, system: str, login_id: str, app_token: str, dry_run: bool = True
):
    successful_transformations = []
    failed_transformations = []

    context = CoraContext(
        system=system,
        login_id=login_id,
        app_token=app_token,
    )

    context.log("==== Begin processing Fedora XML publications ====")
    context.log(
        f"==== xml_dir={xml_dir}, system={system}, login_id={login_id}, dry_run={dry_run} ===="
    )
    context.log("==================================================")

    files = [filename for filename in os.listdir(xml_dir) if filename.endswith(".xml")]

    def process_file(filename):
        context.log(f"--- Processing file: {filename} ---")
        try:
            source_record = _read_source_record_from_file(xml_dir, filename)
            valid, errors = output_migrate(source_record, context, xml_dir, dry_run)
            if valid:
                successful_transformations.append(filename)
            else:
                failed_transformations.append(
                    f"{filename} - Errors: [{', '.join(errors) if errors else ''}]"
                )
        except Exception as e:
            failed_transformations.append(f"{filename} - Exception: {str(e)}")

    run_with_threads(
        files,
        process_file,
        workers=8,
        desc="Processing publication files",
    )

    context.log("==== Processing complete ====")

    context.log(f"{len(successful_transformations)} Successful transformations:")
    for filename in successful_transformations:
        context.log(f"✅ {filename}")

    context.log(f"{len(failed_transformations)} Failed transformations:")
    for filename in failed_transformations:
        context.log(f"❌ {filename}")

    print(
        f"{len(successful_transformations)} succeeded, {len(failed_transformations)} failed."
    )
    print(f"Output logged to {context.get_logger().handlers[0].baseFilename}")  # type: ignore[attr-defined]


def _read_source_record_from_file(xml_dir, filename):
    filepath = os.path.join(xml_dir, filename)
    source_record = read_source_xml(filepath)
    return source_record
