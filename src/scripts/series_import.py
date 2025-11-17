import time
from common.arg_parser import create_argument_parser, common_arguments
from common.xml_utils import transform_record_list
from cora.context import CoraContext, Context
from common import common_data
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.series_transform import transform_series

RECORD_TYPE = "diva-series"


def main():
    parser = create_argument_parser(
        description="Import series from XML",
        arguments=common_arguments,
    )

    args = parser.parse_args()

    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    series_import(context, args.xml_path, args.apply)


def series_import(context: Context, xml_path: str, apply: bool):
    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context, xml_path)

    cora_series = transform_record_list(source_records, transform_series, context)

    validation_results = validate_record_list(cora_series, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_series, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )
    valid_count = sum(1 for valid, _ in validation_results if valid)
    invalid_count = sum(1 for valid, _ in validation_results if not valid)
    print(f"✅ {valid_count} valid")
    print(f"❌ {invalid_count} invalid")


def _read_source_records(context: Context, xml_path: str):
    source_data = common_data.read_source_xml(xml_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


if __name__ == "__main__":
    main()
