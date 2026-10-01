import os
from unittest import result
from common.arg_parser import create_argument_parser, common_arguments
from common.environment import load_environment
from common.common_data import read_source_xml
from common.logging_config import configure_logging
from cora.context import CoraContext
from cora.create import create_record, is_success_result


def main():
    load_environment()
    parser = create_argument_parser(
        description="Create Cora test outputs",
        arguments={
            "--xml-dir": {
                "default": "data/cora/testdata",
                "help": "Directory containing XML files to process",
            },
            **{
                name: common_arguments[name]
                for name in ("--cora-url", "--system", "--login-id", "--app-token")
            },
        },
    )

    args = parser.parse_args()

    configure_logging()

    env = {
        "xml_dir": args.xml_dir,
        "system": args.system,
        "login_id": args.login_id,
        "app_token": args.app_token,
        "cora_url": args.cora_url,
    }

    process_cora_testdata_files(**env)


def process_cora_testdata_files(
    xml_dir: str,
    system: str,
    login_id: str,
    app_token: str,
    cora_url: str | None = None,
):

    context = CoraContext(
        system=system,
        login_id=login_id,
        app_token=app_token,
        cora_url=cora_url,
    )

    for filename in os.listdir(xml_dir):
        if filename.endswith(".xml"):
            process_file(xml_dir, filename, context)


def process_file(xml_dir: str, filename: str, context: CoraContext):
    print(f"Processing {filename}...")
    filepath = os.path.join(xml_dir, filename)
    source_record = read_source_xml(filepath)
    result = create_record(
        source_record,
        record_type="diva-output",
        context=context,
    )
    if is_success_result(result):
        print(f"✅ Successfully created record for {filename}")
    else:
        print(f"❌ Failed to create record for {filename}: {result.error}")


if __name__ == "__main__":
    main()
