import argparse
import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.publisher_transform import transform_publisher
from common.arg_parser import create_argument_parser

RECORD_TYPE = "diva-publisher"

DEFAULT_ENV = {
    "xml_path": "data/db_xml/publishers.xml",
    "system": "preview",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
    "apply": False,
    "workers": 16,
}


def main():
    """Main entry point for the publishers import script."""
    parser = create_argument_parser(
        description="Process publisher db xml files and import them to Cora",
        arguments={
            "--xml-path": {
                "default": DEFAULT_ENV["xml_path"],
                "help": "Path to XML containing publisher source data",
            },
            "--system": {
                "default": DEFAULT_ENV["system"],
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": DEFAULT_ENV["login_id"],
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "default": DEFAULT_ENV["app_token"],
                "help": "Application token for authentication",
            },
            "--workers": {
                "type": int,
                "default": DEFAULT_ENV["workers"],
                "help": "Number of worker threads",
            },
            "--apply": {
                "action": "store_true",
                "help": "Perform actual transformations (default is dry run)",
            },
        },
    )
    args = parser.parse_args()

    context = CoraContext(args.system, args.login_id, args.app_token)

    publishers_import(
        context,
        xml_path=args.xml_path,
        workers=args.workers,
        apply=args.apply,
    )


def publishers_import(context: Context, xml_path: str, workers: int, apply: bool):

    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context, xml_path)

    cora_publishers = _transform_to_cora_publishers(source_records, workers)

    validation_results = validate_record_list(cora_publishers, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_publishers, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context, xml_path: str):
    source_data = common_data.read_source_xml(xml_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_publishers(source_records: list[ET.Element], workers: int):
    return run_with_threads(
        source_records,
        transform_publisher,
        workers=workers,
        desc="Transforming new records",
    )


if __name__ == "__main__":
    main()
