import time
from common.xml_utils import transform_record_list
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.funder_transform import transform_funder
from common.arg_parser import create_argument_parser, common_arguments

RECORD_TYPE = "diva-funder"


def main():
    parser = create_argument_parser(
        description="Import funder data from XML",
        arguments=common_arguments,
    )

    args = parser.parse_args()

    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    funders_import(xml_path=args.xml_path, context=context, apply=args.apply)


def funders_import(xml_path: str, context: Context, apply: bool):
    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(xml_path, context)

    cora_funders = transform_record_list(source_records, transform_funder, context)

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


if __name__ == "__main__":
    main()
