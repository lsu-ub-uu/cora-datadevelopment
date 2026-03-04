import xml.etree.ElementTree as ET
from common.xml_utils import create_text
from fedora_to_cora.transform.get_content_type import get_content_type


def create_genre_type_content_type(source_record: ET.Element) -> ET.Element | None:
    content_type_code = source_record.find("./contentType/contentTypeCode")
    if content_type_code is None or content_type_code.text is None:
        return None

    content_type = get_content_type(content_type_code.text)

    return create_text(
        "genre",
        type="contentType",
        value=content_type,
    )
