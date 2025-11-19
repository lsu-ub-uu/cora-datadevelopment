import os
from typing import Callable, Union, Dict, List, TypedDict, Optional
import xml.etree.ElementTree as ET
import xml.dom.minidom

from cora.context import Context


def pretty_print_xml_string(xml_string: str) -> str:
    reparsed = xml.dom.minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    lines = [line for line in pretty_xml.split("\n")[1:] if line.strip()]
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(lines)


def pretty_print_xml(element: ET.Element) -> str:
    """
    Convert an XML Element to a pretty-printed XML string.
    """
    ET.indent(element)
    return ET.tostring(element, encoding="unicode")


def inline_xml_string(xml: str) -> str:
    """
    Convert a multi-line XML string into a single line string suitable for inline use.
    """
    return "".join(line.strip() for line in xml.splitlines() if line.strip())


def get_inner_xml(element: ET.Element) -> str:
    return "".join(ET.tostring(child, encoding="unicode") for child in element)


def append_if_value(
    parent: ET.Element, child: ET.Element | list[ET.Element] | None
) -> None:
    """
    Append a child element or list of child elements to a parent if they are not None and have content.
    """
    if child is None:
        return

    if isinstance(child, list):
        for element in child:
            if element is not None and (len(element) > 0 or element.text):
                parent.append(element)
    else:
        if len(child) > 0 or child.text:
            parent.append(child)


def save_to_file(xml: ET.Element, filename: str) -> None:
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    ET.indent(xml)
    tree = ET.ElementTree(xml)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


def transform_record_list(
    source_records: list[ET.Element],
    transform_function: Callable[[ET.Element], ET.Element],
    context: Context,
) -> list[ET.Element]:
    success = True
    results: list[ET.Element] = []
    for source_record in source_records:
        try:
            results.append(transform_function(source_record))
        except Exception as e:
            context.log(
                f"Error transforming record with oldId {source_record.findtext("old_id")}: {str(e)}",
                "error",
            )
            success = False
            continue

    if not success:
        raise Exception("One or more records failed to transform.")

    return results
