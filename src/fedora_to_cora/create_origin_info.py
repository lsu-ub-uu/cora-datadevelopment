import xml.etree.ElementTree as ET


def create_origin_info(source_record: ET.Element) -> ET.Element | None:
    """
    Create an origin_info element
    """
    origin_info = ET.Element("originInfo")
    date_issued = create_date_issued(source_record)

    if date_issued is not None:
        origin_info.append(date_issued)

    # TODO copyrightDate
    # TODO dateOther type="online"
    # TODO agent
    # TODO place
    # TODO edition

    if len(origin_info) == 0:
        return None

    return origin_info


def create_date_issued(source_record: ET.Element) -> ET.Element | None:
    """
    Create a date_issued element
    """
    source_date_issued = source_record.find("./dateIssued")
    if source_date_issued is None or source_date_issued.text is None:
        return None

    date_issued = ET.Element("dateIssued")
    ET.SubElement(date_issued, "year").text = source_date_issued.text

    return date_issued
