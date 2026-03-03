import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_date import create_date


def create_date_other_type_patent(source_record: ET.Element) -> ET.Element | None:
    date_source = source_record.findtext("./patentDate")

    return create_date(date_source, "dateOther", type="patent")
