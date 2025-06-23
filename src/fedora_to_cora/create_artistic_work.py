import xml.etree.ElementTree as ET


def create_artistic_work(source_record: ET.Element) -> ET.Element | None:
    """
    Create an artisticWork element from the source record.
    """

    source = source_record.find(".//artisticWork")
    if source is None or source.text is None:
        return None

    artistic_work = ET.Element("artisticWork", type="outputType")
    artistic_work.text = source.text
    return artistic_work
