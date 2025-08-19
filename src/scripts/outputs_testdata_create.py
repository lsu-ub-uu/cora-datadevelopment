import argparse
import os
from common.common_data import read_source_xml
from cora.context import CoraContext
from cora.create import create_record

# Default environment configuration
DEFAULT_ENV = {
    "xml_dir": "data/cora/testdata",
    "system": "preview",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
}


def main():
    parser = argparse.ArgumentParser(description="Create Cora test outputs")

    parser.add_argument(
        "--xml-dir",
        default=DEFAULT_ENV["xml_dir"],
        help=f"Directory containing XML files to process (default: {DEFAULT_ENV['xml_dir']})",
    )

    parser.add_argument(
        "--system",
        default=DEFAULT_ENV["system"],
        help=f"Target system (default: {DEFAULT_ENV['system']})",
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

    args = parser.parse_args()

    env = {
        "xml_dir": args.xml_dir,
        "system": args.system,
        "login_id": args.login_id,
        "app_token": args.app_token,
    }

    process_cora_testdata_files(**env)


def process_cora_testdata_files(
    xml_dir: str,
    system: str,
    login_id: str,
    app_token: str,
):

    context = CoraContext(
        system=system,
        login_id=login_id,
        app_token=app_token,
    )

    for filename in os.listdir(xml_dir):
        if filename.endswith(".xml"):
            process_file(xml_dir, filename, context)


def process_file(xml_dir: str, filename: str, context: CoraContext):
    print(f"Processing {filename}...")
    filepath = os.path.join(xml_dir, filename)
    source_record = read_source_xml(filepath)
    valid, errors = create_record(
        source_record,
        record_type="diva-output",
        context=context,
    )
    if valid:
        print(f"✅ Successfully created record for {filename}")
    else:
        print(f"❌ Failed to create record for {filename}: {errors}")


if __name__ == "__main__":
    main()
