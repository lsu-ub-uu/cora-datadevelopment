import xml.etree.ElementTree as ET
from fedora_to_cora.get_content_type import get_content_type


def create_genre_type_content_type(source_record):
    attributes = {"type": "contentType"}
    old_variable = source_record.find(".//contentTypeCode")
    old_content = get_content_type(old_variable.text)
    genre = ET.Element("genre", attrib=attributes)
    genre.text = old_content

    return genre
