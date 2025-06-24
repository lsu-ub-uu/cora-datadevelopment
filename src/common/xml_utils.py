import xml.etree.ElementTree as ET
import xml.dom.minidom


def pretty_print_xml(element: ET.Element) -> str:
    """
    Convert an XML Element to a pretty-printed XML string.
    """
    xml_string = ET.tostring(element, encoding="utf-8", method="xml")
    reparsed = xml.dom.minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(
        pretty_xml.split("\n")[1:]
    )


def inline_xml_string(xml: str) -> str:
    """
    Convert a multi-line XML string into a single line string suitable for inline use.
    """
    return "".join(line.strip() for line in xml.splitlines() if line.strip())
