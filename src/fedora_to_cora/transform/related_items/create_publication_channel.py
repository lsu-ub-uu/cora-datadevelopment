import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_publication_channel(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "relatedItem",
        type="publicationChannel",
        children=[create_text("publicationChannel", source_record.findtext("publicationChannel"))],
    )