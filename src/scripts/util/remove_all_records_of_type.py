from cora.context import CoraContext
import requests
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from common.arg_parser import create_argument_parser, common_arguments
from common.environment import load_environment
from common.logging_config import configure_logging


def main():
    load_environment()
    argparser = create_argument_parser(
        description=f"Remove all records of a record type from Cora",
        arguments={
            **common_arguments,
            "--record-type": {
                "help": "Type of records to remove (e.g., 'diva-output', 'diva-person', 'diva-organisation')",
                "type": str,
            },
        },
    )

    args = argparser.parse_args()

    configure_logging()
    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
        cora_url=args.cora_url,
    )

    response = requests.get(
        f"{context.get_base_url()}/{args.record_type}",
        headers={
            "Authtoken": context.get_auth_token(),
            "Accept": "application/vnd.cora.recordList+xml",
        },
    )

    response.raise_for_status()

    record_list_xml = ET.fromstring(response.text)
    record_ids = record_list_xml.findall("./data/record/data/*/recordInfo/id")

    if not args.apply:
        print(
            f"Found {len(record_ids)} records of type {args.record_type}. Run the script with --apply to delete them."
        )
        return

    # Extra confirmation prompt
    print(
        f"WARNING: You are about to delete {len(record_ids)} records of type {args.record_type} in the Cora system at [{context.get_base_url()}]."
    )
    confirmation = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if confirmation not in ["yes", "y"]:
        print("Deletion cancelled.")
        return

    def delete_record(record_id_elem):
        record_id = record_id_elem.text
        requests.delete(
            f"{context.get_base_url()}/{args.record_type}/{record_id}",
            headers={
                "Authtoken": context.get_auth_token(),
            },
        )

    run_with_threads(
        record_ids, delete_record, context.get_workers(), "Deleting records"
    )
    print(f"Deleted {len(record_ids)} records of type {args.record_type}.")


if __name__ == "__main__":
    main()
