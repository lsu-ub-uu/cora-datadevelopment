import xml.etree.ElementTree as ET


def create_end_date(date: str, origin_type: str | None = None) -> ET.Element:
    """
    Create a Cora end date element from a source record.
    """
    end_date = ET.Element("endDate")
    year, month, day = map(str.strip, date.split("-"))
    
    end_date.append(
        create_element("year", year),
        )
    end_date.append(
        create_element("month", month),
        )
    end_date.append(
        create_element("day", day),
        )
    
    return end_date


def create_element(tag_name: str, text: str) -> ET.Element:
    element = ET.Element(tag_name)
    element.text = text
    
    return element

