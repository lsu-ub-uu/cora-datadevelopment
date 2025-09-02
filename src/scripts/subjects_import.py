import time
from common.arg_parser import create_argument_parser
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.subject_transform import transform_subject

RECORD_TYPE = "diva-subject"


def main():
    parser = create_argument_parser(
        description="Import journals from XML",
        arguments={
            "--xml-path": {
                "help": "Path to the XML file containing journal data",
                "required": True,
            },
            "--system": {
                "help": "Cora system to connect to (e.g., 'preview', 'production')",
                "type": str,
                "default": "preview",
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
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )
    subjects_import(context, args.xml_path, args.apply)


def subjects_import(context: Context, xml_path: str, apply: bool):
    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context, xml_path)

    cora_subjects = _transform_to_cora_subjects(source_records)

    validation_results = validate_record_list(cora_subjects, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_subjects, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context, xml_path: str):
    source_data = common_data.read_source_xml(xml_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_subjects(source_records: list[ET.Element]):
    return [transform_subject(source_record) for source_record in source_records]


if __name__ == "__main__":
    main()
