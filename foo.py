from common import common_data;
from xml.etree import ElementTree as ET

def main():
    xml = common_data.read_source_xml("db_xml/funder_from_db.xml")
    print(ET.tostring(xml))

if __name__ == "__main__":
    main()