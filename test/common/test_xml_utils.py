import xml.etree.ElementTree as ET
from common.xml_utils import append_if_value


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
