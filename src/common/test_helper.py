import xml.etree.ElementTree as ET

from common.xml_utils import pretty_print_xml_string


def __normalize_xml_string(xml):
    if isinstance(xml, str):
        root = ET.fromstring(xml)
    else:
        root = xml  # already an Element

    def canonicalize(elem):
        attribs = " ".join(f'{k}="{v}"' for k, v in sorted(elem.attrib.items()))
        start_tag = f"<{elem.tag}{(' ' + attribs) if attribs else ''}>"

        text = (elem.text or "").strip()
        children = "".join(canonicalize(child) for child in elem)
        end_tag = f"</{elem.tag}>"

        return f"{start_tag}{text}{children}{end_tag}"

    return canonicalize(root)


def assert_equal_for_xml_and_xml_string(actual_xml, expected_xml):
    expected_as_xml = ET.fromstring(expected_xml)
    expected_normalized = pretty_print_xml_string(
        __normalize_xml_string(expected_as_xml)
    )
    actual_xml_normalized = pretty_print_xml_string(__normalize_xml_string(actual_xml))

    assert actual_xml_normalized == expected_normalized
