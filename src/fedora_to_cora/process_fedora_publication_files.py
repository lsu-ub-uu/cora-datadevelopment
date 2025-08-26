from common.common_data import read_source_xml
import os
import traceback
from common.threads import run_with_threads
from cora.context import CoraContext, Context
from fedora_to_cora.output_migrate import output_migrate

successful_transformations = []
failed_transformations = []


def process_fedora_publication_files(
    xml_dir: str, system: str, login_id: str, app_token: str, dry_run: bool = True
):
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

    run_with_threads(
        os.listdir(xml_dir),
        lambda filename: _process_file(filename, context, xml_dir, dry_run),
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


def _process_file(filename: str, context: Context, xml_dir: str, dry_run: bool):
    context.log(f"--- Processing file: {filename} ---")
    if not filename.endswith(".xml"):
        context.log(f"Skipping non-XML file: {filename}")
        return
    source_record = _read_source_record_from_file(xml_dir, filename)
    valid, errors = output_migrate(source_record, context, xml_dir, dry_run)
    if valid:
        successful_transformations.append(filename)
    else:
        failed_transformations.append(
            f"{filename} - Errors: [{', '.join(errors) if errors else ''}]"
        )


def _read_source_record_from_file(xml_dir, filename):
    filepath = os.path.join(xml_dir, filename)
    source_record = read_source_xml(filepath)
    return source_record
