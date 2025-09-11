from common.xml_utils import save_to_file
from classic.get_journals import get_journals
from datetime import datetime
import getpass


def main():
    db_user = input("Enter DB user: ")
    if db_user == None or len(db_user) == 0:
        print("No DB user entered")
        return

    password = getpass.getpass("Enter DB password: ")
    if password == None or len(password) == 0:
        print("No password entered")
        return

    print("Password entered. Starting export...")
    journals = get_journals(db_user=db_user, db_password=password)
    filename = f"data/db_xml/journals_{_get_now().isoformat()}.xml"
    save_to_file(journals, filename)
    print(f"--- Successfully exported journals to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
