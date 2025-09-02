import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.journal_transform import transform_journal
from common.arg_parser import create_argument_parser, common_arguments

RECORD_TYPE = "diva-journal"


def main():

    parser = create_argument_parser(
        description="Import journals from XML",
        arguments=common_arguments,
    )

    args = parser.parse_args()

    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    journals_import(context, args.xml_path, args.apply)


def journals_import(context: Context, xml_path: str, apply: bool):
    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context, xml_path)

    cora_journals = _transform_to_cora_journals(source_records)

    validation_results = validate_record_list(cora_journals, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_journals, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context, xml_path: str):
    source_data = common_data.read_source_xml(xml_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_journals(source_records: list[ET.Element]):
    return [transform_journal(record) for record in source_records]


if __name__ == "__main__":
    main()
