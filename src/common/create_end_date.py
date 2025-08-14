import xml.etree.ElementTree as ET

def create_end_date(date: str) -> ET.Element:
    """
    Create a Cora end date element from a source record.
    """
    
    end_date = ET.Element("endDate")
    year, month, day = map(str.strip, date.split("-"))
    
    append_year_month_day(end_date, year, month, day)

    return end_date

def append_year_month_day(element: ET.Element, year: str, month: str, day:str):
    element.append(
        create_element("year", year))
    element.append(
        create_element("month", month))
    element.append(
        create_element("day", day))
    
    
def create_element(tag_name: str, text: str) -> ET.Element:
    element = ET.Element(tag_name)
    element.text = text
    
    return element
    