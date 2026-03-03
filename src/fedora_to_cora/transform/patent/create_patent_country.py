import xml.etree.ElementTree as ET
from common.xml_utils import create_text


def create_patent_country(source_record: ET.Element) -> ET.Element | None:
    return create_text(
        "patentCountry", source_record.findtext("./patentCountry/countryCode")
    )
