import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_date import create_date

def create_date_other_type_patent(source_record: ET.Element) -> ET.Element:
    date_source = source_record.find("./patentDate")

    date_other = ET.Element("dateOther", type="patent")

    if date_source is not None and date_source.text:
        return create_date(date_source.text, "dateOther", type="patent")

    return date_other
