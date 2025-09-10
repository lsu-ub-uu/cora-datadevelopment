import xml.etree.ElementTree as ET
import re
from common.xml_utils import pretty_print_xml_string


def assert_equal_for_xml_and_xml_string(actual_xml, expected_xml):
    expected_as_xml = ET.fromstring(expected_xml)
    expected_normalized = pretty_print_xml_string(
        _normalize_xml_string(expected_as_xml)
    )
    actual_xml_normalized = pretty_print_xml_string(_normalize_xml_string(actual_xml))

    assert actual_xml_normalized == expected_normalized


def assert_equal_for_sql(expected_sql_query: str, actual_sql_query: str):
    expected_normalized = _normalize_sql_query(expected_sql_query)
    actual_normalized = _normalize_sql_query(actual_sql_query)

    assert expected_normalized == actual_normalized


def _normalize_xml_string(xml):
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


def _normalize_sql_query(sql_query: str) -> str:
    # Remove SQL comments (both -- and /* */ style)
    # Remove single-line comments (-- comment)
    sql_query = re.sub(r"--.*$", "", sql_query, flags=re.MULTILINE)

    # Remove multi-line comments (/* comment */)
    sql_query = re.sub(r"/\*.*?\*/", "", sql_query, flags=re.DOTALL)

    # Replace multiple whitespace characters (including newlines) with single spaces
    sql_query = re.sub(r"\s+", " ", sql_query)

    # Remove leading and trailing whitespace
    sql_query = sql_query.strip()

    return sql_query
