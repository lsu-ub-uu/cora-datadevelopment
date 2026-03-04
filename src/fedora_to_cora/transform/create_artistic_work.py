import xml.etree.ElementTree as ET

from common.xml_utils import create_text


def create_artistic_work(source_record: ET.Element) -> ET.Element | None:
    """
    Create an artisticWork element from the source record.
    """

    return create_text(
        "artisticWork",
        type="outputType",
        value=source_record.findtext("./artisticWork"),
    )
