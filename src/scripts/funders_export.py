from common.arg_parser import create_argument_parser
from common.xml_utils import save_to_file
from classic.get_funders import get_funders
from datetime import datetime
import getpass
import xml.etree.ElementTree as ET


def main():
    db_user = input("Enter DB user (default 'readOnlyUser'): ") or "readOnlyUser"
    password = getpass.getpass("Enter DB password: ")
    print("Password entered. Starting export...")
    print(db_user, password)
    funders = get_funders(db_user=db_user, db_password=password)
    filename = f"data/db_xml/funders_{_get_now().isoformat()}.xml"
    save_to_file(funders, filename)
    print(f"--- Successfully exported funders to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
