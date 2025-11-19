from common.arg_parser import create_argument_parser
from common.xml_utils import save_to_file
from classic.get_subjects import get_subjects
from datetime import datetime
import getpass


def main():
    argparser = create_argument_parser(
        description="Export subjects from DiVA Classic",
        arguments={
            "--domain": {
                "help": "Domain to export subjects from",
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
    subjects = get_subjects(
        domain=args.domain, db_user=args.db_user, db_password=args.db_password
    )
    filename = f"data/db_xml/subjects_{args.domain}_{_get_now().isoformat()}.xml"
    save_to_file(subjects, filename)
    print(f"--- Successfully exported subjects to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
