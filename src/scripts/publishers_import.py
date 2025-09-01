import argparse
import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.publisher_transform import transform_publisher

RECORD_TYPE = "diva-publisher"

DEFAULT_ENV = {
    "source_xml_path": "data/db_xml/publishers.xml",
    "target_system": "preview",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
    "apply": False,
    "workers": 16,
}


def main():
    """Main entry point for the publishers import script."""
    parser = argparse.ArgumentParser(
        description="Process publisher db xml files and import them to Cora"
    )

    parser.add_argument(
        "--xml-dir",
        default=DEFAULT_ENV["xml_dir"],
        help=f"Directory containing XML files to process (default: {DEFAULT_ENV['xml_dir']})",
    )

    parser.add_argument(
        "--system",
        default=DEFAULT_ENV["system"],
        help=f"Target system for migration (default: {DEFAULT_ENV['system']})",
    )

    parser.add_argument(
        "--login-id",
        default=DEFAULT_ENV["login_id"],
        help=f"Login ID for authentication (default: {DEFAULT_ENV['login_id']})",
    )

    parser.add_argument(
        "--app-token",
        default=DEFAULT_ENV["app_token"],
        help="Application token for authentication (default: uses preset token)",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform actual transformations (default is dry run)",
    )

    args = parser.parse_args()

    env = {
        "xml_dir": args.xml_dir,
        "system": args.system,
        "login_id": args.login_id,
        "app_token": args.app_token,
        "apply": args.apply,
    }


def publishers_import(context: Context, xml_directory: str, workers: int, apply: bool):
    context = CoraContext(system, login_id, app_token)

    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context)

    cora_publishers = _transform_to_cora_publishers(source_records)

    validation_results = validate_record_list(cora_publishers, RECORD_TYPE, context)

    if not apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_publishers, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context):
    source_data = common_data.read_source_xml(xml_dir)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_publishers(source_records: list[ET.Element]):
    return run_with_threads(
        source_records,
        transform_publisher,
        workers=workers,
        desc="Transforming new records",
    )


if __name__ == "__main__":
    main()
