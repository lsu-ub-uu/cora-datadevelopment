from xml.etree import ElementTree as ET

def create_date(date_source: str, tag_name: str, **attribs) -> ET.Element:
    if (date_source is None) or (date_source.strip() == ""):
        return None
    
    date_element = ET.Element(tag_name, attrib=attribs)

    date_part = date_source.split("T")[0]
    year, month, day = date_part.split("-")

    year_element = ET.SubElement(date_element, "year")
    year_element.text = year

    month_element = ET.SubElement(date_element, "month")
    month_element.text = month

    day_element = ET.SubElement(date_element, "day")
    day_element.text = day

    return date_element