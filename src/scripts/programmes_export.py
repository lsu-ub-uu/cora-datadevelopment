from common.arg_parser import create_argument_parser
from common.xml_utils import save_to_file
from classic.get_programmes import get_programmes
from datetime import datetime
import getpass


def main():
    argparser = create_argument_parser(
        description="Export programmes from DiVA Classic",
        arguments={
            "--domain": {
                "help": "Domain to export programmes from",
                "type": str,
                "required": True,
            }
        },
    )
    args = argparser.parse_args()

    db_user = input("Enter DB user: ")
    if db_user == None or len(db_user) == 0:
        print("No DB user entered")
        return

    password = getpass.getpass("Enter DB password: ")
    if password == None or len(password) == 0:
        print("No password entered")
        return

    print("Password entered. Starting export...")
    programmes = get_programmes(
        domain=args.domain, db_user=db_user, db_password=password
    )
    filename = f"data/db_xml/programmes_{_get_now().isoformat()}.xml"
    save_to_file(programmes, filename)
    print(f"--- Successfully exported programmes to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
