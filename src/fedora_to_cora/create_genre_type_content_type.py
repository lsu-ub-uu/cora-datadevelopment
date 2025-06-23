import xml.etree.ElementTree as ET
from fedora_to_cora.get_content_type import get_content_type


def create_genre_type_content_type(source_record: ET.Element) -> ET.Element | None:
    content_type_code = source_record.find(".//contentTypeCode")
    if content_type_code is None or content_type_code.text is None:
        return None

    old_content = get_content_type(content_type_code.text)

    genre = ET.Element("genre", type="contentType")
    genre.text = old_content

    return genre
