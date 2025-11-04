import xml.etree.ElementTree as ET


def create_date_other_type_patent(source_record: ET.Element) -> ET.Element:
    date_source = source_record.find("./patentDate")

    date_other = ET.Element("dateOther", type="patent")

    if date_source is not None and date_source.text:
        date_part = date_source.text.split("T")[0]
        year, month, day = date_part.split("-")

        year_element = ET.SubElement(date_other, "year")
        year_element.text = year

        month_element = ET.SubElement(date_other, "month")
        month_element.text = month

        day_element = ET.SubElement(date_other, "day")
        day_element.text = day
    return date_other
