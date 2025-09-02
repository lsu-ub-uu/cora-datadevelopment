import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.funder_transform import transform_funder
from common.arg_parser import create_argument_parser

RECORD_TYPE = "diva-funder"


def main():
    parser = create_argument_parser(
        description="Import funder data from XML",
        arguments={
            "--xml-path": {
                "help": "Path to the XML file containing funder data",
                "default": "data/db_xml/funders.xml",
            },
            "--system": {
                "help": "Cora system to connect to (e.g., 'preview', 'production')",
                "type": str,
                "default": "pre",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "default": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
                "help": "Application token for authentication",
            },
            "--apply": {
                "help": "Apply changes to the Cora system (dry run if not present)",
                "action": "store_true",
            },
            "--workers": {
                "help": "Number of worker threads for processing",
                "type": int,
                "default": 16,
            },
        },
    )

    args = parser.parse_args()

    context = CoraContext(
        system=args.system, login_id=args.login_id, app_token=args.app_token
    )

    funders_import(
        xml_path=args.xml_path, workers=args.workers, context=context, apply=args.apply
    )


def funders_import(xml_path: str, workers: int, context: Context, apply: bool):
    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(xml_path, context)

    cora_funders = _transform_to_cora_funders(source_records, workers)

    validation_results = validate_record_list(cora_funders, RECORD_TYPE, context)

    if not apply:
        print("Skipped creating records, because not running in --apply mode")
    elif not all(valid for (valid, _) in validation_results):
        print("Skipped creating records, because there were validation failures")
    else:
        print("All records are valid. Proceeding with creation.")
        create_record_list(cora_funders, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(xml_path, context: Context):
    source_data = common_data.read_source_xml(xml_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_funders(source_records: list[ET.Element], workers: int):
    return run_with_threads(
        source_records,
        transform_funder,
        workers=workers,
        desc="Transforming new records",
    )


if __name__ == "__main__":
    main()
