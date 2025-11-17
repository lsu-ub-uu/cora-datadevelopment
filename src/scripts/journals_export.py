from common.arg_parser import create_argument_parser
from common.xml_utils import save_to_file
from classic.get_journals import get_journals
from datetime import datetime


def main():
    argparser = create_argument_parser(
        description="Export courses from DiVA Classic",
        arguments={
            "--db-user": {
                "help": "Database user for Classic Cora",
                "type": str,
                "required": True,
            },
            "--db-password": {
                "help": "Database password for Classic Cora",
                "type": str,
                "required": True,
            },
        },
    )
    args = argparser.parse_args()

    print("Password entered. Starting export...")
    journals = get_journals(db_user=args.db_user, db_password=args.db_password)
    filename = f"data/db_xml/journals_{_get_now().isoformat()}.xml"
    save_to_file(journals, filename)
    print(f"--- Successfully exported journals to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
