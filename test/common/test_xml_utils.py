import xml.etree.ElementTree as ET
from common.xml_utils import (
    append_if_value,
    create_group,
    transform_text_element,
    create_text,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_append_if_value_appends_element_with_child_node():
    parent = ET.Element("parent")

    child = ET.Element("child")
    ET.SubElement(child, "subchild").text = "value"

    append_if_value(parent, child)
    assert len(parent) == 1
    assert parent[0] == child


def test_append_if_value_with_child_text():
    parent = ET.Element("parent")

    child = ET.Element("child")
    child.text = "text value"

    append_if_value(parent, child)
    assert len(parent) == 1
    assert parent[0] == child


def test_append_if_value_with_empty_child():
    parent = ET.Element("parent")

    child = ET.Element("child")

    append_if_value(parent, child)
    assert len(parent) == 0


def test_append_if_value_with_empty_child2():
    parent = ET.Element("parent")
    child = ET.fromstring("<child />")

    append_if_value(parent, child)
    assert len(parent) == 0


def test_append_if_value_with_none_child():
    parent = ET.Element("parent")

    append_if_value(parent, None)
    assert len(parent) == 0


def test_append_if_value_with_list_of_elements():
    parent = ET.Element("parent")

    child1 = ET.Element("child1")
    child1.text = "text value 1"

    child2 = ET.Element("child2")
    child2.text = "text value 2"

    append_if_value(parent, [child1, child2])

    assert len(parent) == 2
    assert parent[0] == child1
    assert parent[1] == child2


def test_transform_text_element_with_text():
    source = ET.Element("source")
    source.text = "Hello World"
    new_tag = "greeting"
    result = transform_text_element(source, new_tag)
    assert result is not None
    assert result.tag == new_tag
    assert result.text == "Hello World"


def test_transform_text_element_with_empty_text():
    source = ET.Element("source")
    source.text = "   "
    new_tag = "empty"
    result = transform_text_element(source, new_tag)
    assert result is None


def test_transform_text_element_with_no_text():
    source = ET.Element("source")
    new_tag = "empty"
    result = transform_text_element(source, new_tag)
    assert result is None


def test_transform_text_element_with_none_element():
    result = transform_text_element(None, "any")
    assert result is None


def test_create_text_with_text():
    result = create_text("greeting", "Hello World")
    assert result is not None
    assert result.tag == "greeting"
    assert result.text == "Hello World"
    assert_equal_for_xml_and_xml_string(result, "<greeting>Hello World</greeting>")


def test_create_text_removes_newline_and_trims():
    result = create_text("greeting", "  Hello\nWorld  ")
    assert result is not None
    assert result.tag == "greeting"
    assert result.text == "Hello World"
    assert_equal_for_xml_and_xml_string(result, "<greeting>Hello World</greeting>")


def test_create_text_preserve_newlines():
    result = create_text("greeting", "  Hello\nWorld  ", preserve_newlines=True)
    assert result is not None
    assert result.tag == "greeting"
    assert result.text == "Hello\nWorld"
    assert_equal_for_xml_and_xml_string(result, "<greeting>Hello\nWorld</greeting>")


def test_create_text_with_text_and_attributes():
    result = create_text("greeting", "Hello World", lang="en", type="formal")
    assert result is not None
    assert result.tag == "greeting"
    assert result.text == "Hello World"
    assert result.attrib == {"lang": "en", "type": "formal"}
    assert_equal_for_xml_and_xml_string(
        result, '<greeting lang="en" type="formal">Hello World</greeting>'
    )


def test_create_text_returns_none_when_text_is_none():
    result = create_text("greeting", None)
    assert result is None


def test_create_text_returns_none_when_text_is_empty():
    result = create_text("greeting", "")
    assert result is None


def test_create_group_element_without_elements():
    result = create_group("group", [])
    assert result is None


def test_create_group_with_elements():
    result = create_group(
        "group",
        [
            create_text("child1", "Value 1"),
            create_text("child2", "Value 2"),
        ],
    )
    assert_equal_for_xml_and_xml_string(
        result, "<group ><child1>Value 1</child1><child2>Value 2</child2></group>"
    )


def test_create_group_with_none():
    result = create_group(
        "group",
        [None],
    )
    assert result is None


def test_create_group_with_mixed_value_and_none_elements():
    result = create_group(
        "group",
        [
            create_text("child1", "Value 1"),
            None,
        ],
    )
    assert_equal_for_xml_and_xml_string(
        result, "<group ><child1>Value 1</child1></group>"
    )


def test_create_group_with_elements_and_attributes():
    result = create_group(
        "group",
        [
            create_text("child1", "Value 1"),
            create_group(
                "childGroup",
                [create_text("subChild", "SubValue")],
                lang="en",
            ),
            create_text("child2", "Value 2"),
        ],
        lang="en",
        type="example",
    )
    assert_equal_for_xml_and_xml_string(
        result,
        """
        <group lang='en' type='example'>
            <child1>Value 1</child1>
            <childGroup lang='en'>
                <subChild>SubValue</subChild>
            </childGroup>
            <child2>Value 2</child2>
        </group>
        """,
    )


def test_create_group_flattens_list_children():
    result = create_group(
        "group",
        [
            create_text("child1", "Value 1"),
            [
                create_text("child2", "Value 2"),
                create_text("child3", "Value 3"),
            ],
        ],
    )
    assert_equal_for_xml_and_xml_string(
        result,
        """
        <group >
            <child1>Value 1</child1>
            <child2>Value 2</child2>
            <child3>Value 3</child3>
        </group>
        """,
    )
