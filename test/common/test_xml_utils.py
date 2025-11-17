import xml.etree.ElementTree as ET

import pytest
from common.xml_utils import append_if_value, transform_record_list
from cora.context import MockContext


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


def test_transform_record_list():
    source_records = [
        ET.Element("record1"),
        ET.Element("record2"),
    ]

    def transform_function(record: ET.Element) -> ET.Element:
        return ET.Element("transformed-" + record.tag)

    results = transform_record_list(
        source_records, transform_function, context=MockContext()
    )

    assert len(results) == 2
    assert results[0][0] == source_records[0]
    assert results[1][0] == source_records[1]

    assert results[0][1].tag == "transformed-record1"
    assert results[1][1].tag == "transformed-record2"


def test_transform_record_list_with_error():
    source_records = [
        ET.fromstring("<record1><old_id>1</old_id></record1>"),
        ET.fromstring("<record2><old_id>2</old_id></record2>"),
    ]

    def transform_function(record: ET.Element) -> ET.Element:
        if record.tag == "record2":
            raise ValueError("Transformation error")
        return ET.Element("transformed-" + record.tag)

    mock_context = MockContext()
    with pytest.raises(Exception):
        transform_record_list(source_records, transform_function, context=mock_context)
        mock_context.log.assert_called_with(  # type: ignore
            "Error transforming record with oldId 2: Transformation error",
            "error",
        )
