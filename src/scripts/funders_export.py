from common.arg_parser import create_argument_parser, common_arguments
from common.xml_utils import save_to_file
from classic.get_funders import get_funders
from datetime import datetime


def main():
    funders = get_funders()
    filename = f"data/db_xml/funders_{_get_now().isoformat()}.xml"
    save_to_file(funders, filename)
    print(f"--- Successfully exported funders to {filename} ---")


def _get_now():
    return datetime.now()


if __name__ == "__main__":
    main()
