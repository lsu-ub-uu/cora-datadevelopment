from common.arg_parser import create_argument_parser
from common.xml_utils import save_to_file
from classic.get_series import get_series
from datetime import datetime
import getpass
import xml.etree.ElementTree as ET


def main():
    argparser = create_argument_parser(
        description="Export series from DiVA Classic",
        arguments={
            "--domain": {
                "help": "Domain to export series from",
                "type": str,
                "required": True,
            },
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
    series = get_series(
        domain=args.domain, db_user=args.db_user, db_password=args.db_password
    )
    filename = f"data/db_xml/series_{_get_now().isoformat()}.xml"
    save_to_file(series, filename)
    print(f"--- Successfully exported series to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
