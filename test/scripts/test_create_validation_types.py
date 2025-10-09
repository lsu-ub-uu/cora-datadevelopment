import xml.etree.ElementTree as ET

import pytest

from scripts.create_new_validationTypes import (
    RecordNode, parse_record_from_xml, find_child_urls,
    normalize_regex_patterns, normalize_child_reference_repeat,
    update_child_references, update_record_id_in_xml, remove_action_links,
    create_new_id_and_update_mapping, skip_if_already_processed,
    process_graph_bottom_up_and_store, link_parent_child_relationship,
    find_top_level_children, clean_and_unwrap_xml, remove_unwanted_elements,
    to_xml_bytes
)


@pytest.fixture
def sample_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<record>
    <data>
        <metadata type="group">
            <recordInfo>
                <id>divaTextNewGroup</id>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>metadataGroup</linkedRecordId>
                    <actionLinks>
                        <read>
                            <requestMethod>GET</requestMethod>
                            <rel>read</rel>
                            <url>http://HOSTURL/validationType/metadataGroup</url>
                            <accept>application/vnd.cora.record+xml</accept>
                        </read>
                    </actionLinks>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>diva</linkedRecordId>
                    <actionLinks>
                        <read>
                            <requestMethod>GET</requestMethod>
                            <rel>read</rel>
                            <url>http://HOSTURL/system/diva</url>
                            <accept>application/vnd.cora.record+xml</accept>
                        </read>
                    </actionLinks>
                </dataDivider>
                <type>
                    <linkedRecordType>recordType</linkedRecordType>
                    <linkedRecordId>metadata</linkedRecordId>
                    <actionLinks>
                        <read>
                            <requestMethod>GET</requestMethod>
                            <rel>read</rel>
                            <url>http://HOSTURL/recordType/metadata</url>
                            <accept>application/vnd.cora.record+xml</accept>
                        </read>
                    </actionLinks>
                </type>
                <updated repeatId="0">
                    <updatedBy>
                        <linkedRecordType>user</linkedRecordType>
                        <linkedRecordId>161616</linkedRecordId>
                    </updatedBy>
                    <tsUpdated>2023-10-10T12:17:16.405577Z</tsUpdated>
                </updated>
                <updated repeatId="1">
                    <updatedBy>
                        <linkedRecordType>user</linkedRecordType>
                        <linkedRecordId>coraUser:490742519075086</linkedRecordId>
                    </updatedBy>
                    <tsUpdated>2024-02-27T11:14:19.805743Z</tsUpdated>
                </updated>
                <createdBy>
                    <linkedRecordType>user</linkedRecordType>
                    <linkedRecordId>161616</linkedRecordId>
                </createdBy>
                <tsCreated>2023-10-10T12:17:16.405577Z</tsCreated>
            </recordInfo>
            <nameInData>text</nameInData>
            <regEx>(.*Text$)</regEx>
            <refParentId>
                <linkedRecordType>metadata</linkedRecordType>
                <linkedRecordId>coraTextGroup</linkedRecordId>
                <actionLinks>
                    <read>
                        <requestMethod>GET</requestMethod>
                        <rel>read</rel>
                        <url>http://HOSTURL/coraTextGroup</url>
                        <accept>application/vnd.cora.record+xml</accept>
                    </read>
                </actionLinks>
            </refParentId>
            <childReferences>
                <childReference repeatId="1">
                    <repeatMin>1</repeatMin>
                    <repeatMax>1</repeatMax>
                    <ref>
                        <linkedRecordType>metadata</linkedRecordType>
                        <linkedRecordId>recordInfoNewDivaTextGroup</linkedRecordId>
                        <actionLinks>
                            <read>
                                <requestMethod>GET</requestMethod>
                                <rel>read</rel>
                                <url>
                                    http://HOSTURL/recordInfoNewDivaTextGroup</url>
                                <accept>application/vnd.cora.record+xml</accept>
                            </read>
                        </actionLinks>
                    </ref>
                </childReference>
                <childReference repeatId="2">
                    <repeatMin>1</repeatMin>
                    <repeatMax>1</repeatMax>
                    <ref>
                        <linkedRecordType>metadata</linkedRecordType>
                        <linkedRecordId>textPartSvGroup</linkedRecordId>
                        <actionLinks>
                            <read>
                                <requestMethod>GET</requestMethod>
                                <rel>read</rel>
                                <url>http://HOSTURL/textPartSvGroup</url>
                                <accept>application/vnd.cora.record+xml</accept>
                            </read>
                        </actionLinks>
                    </ref>
                </childReference>
                <childReference repeatId="3">
                    <repeatMin>1</repeatMin>
                    <repeatMax>1</repeatMax>
                    <ref>
                        <linkedRecordType>metadata</linkedRecordType>
                        <linkedRecordId>textPartEnGroup</linkedRecordId>
                        <actionLinks>
                            <read>
                                <requestMethod>GET</requestMethod>
                                <rel>read</rel>
                                <url>http://HOSTURL/textPartEnGroup</url>
                                <accept>application/vnd.cora.record+xml</accept>
                            </read>
                        </actionLinks>
                    </ref>
                </childReference>
            </childReferences>
            <textId>
                <linkedRecordType>text</linkedRecordType>
                <linkedRecordId>divaTextNewGroupText</linkedRecordId>
                <actionLinks>
                    <read>
                        <requestMethod>GET</requestMethod>
                        <rel>read</rel>
                        <url>http://HOSTURL/text/divaTextNewGroupText</url>
                        <accept>application/vnd.cora.record+xml</accept>
                    </read>
                </actionLinks>
            </textId>
            <defTextId>
                <linkedRecordType>text</linkedRecordType>
                <linkedRecordId>divaTextNewGroupDefText</linkedRecordId>
                <actionLinks>
                    <read>
                        <requestMethod>GET</requestMethod>
                        <rel>read</rel>
                        <url>http://HOSTURL/text/divaTextNewGroupDefText</url>
                        <accept>application/vnd.cora.record+xml</accept>
                    </read>
                </actionLinks>
            </defTextId>
        </metadata>
    </data>
    <actionLinks>
        <read>
            <requestMethod>GET</requestMethod>
            <rel>read</rel>
            <url>http://HOSTURL/divaTextNewGroup</url>
            <accept>application/vnd.cora.record+xml</accept>
        </read>
        <read_incoming_links>
            <requestMethod>GET</requestMethod>
            <rel>read_incoming_links</rel>
            <url>http://HOSTURL/divaTextNewGroup/incomingLinks</url>
            <accept>application/vnd.cora.recordList+xml</accept>
        </read_incoming_links>
    </actionLinks>
</record>
"""


@pytest.fixture
def record_node(sample_xml):
    root = ET.fromstring(sample_xml)
    return RecordNode("divaTextNewGroup", "validationType", "http://example.com/record/divaTextNewGroup", root)


# XML Parsing & Node Tests
def test_parse_record_from_xml(sample_xml):
    node = parse_record_from_xml(sample_xml, "http://url")
    assert node.record_id == "divaTextNewGroup"
    assert node.record_type == "metadata"
    assert node.url == "http://url"
    assert isinstance(node.xml_root, ET.Element)


def test_find_child_urls(record_node):
    urls = find_child_urls(record_node.xml_root)
    assert urls == ['http://HOSTURL/recordInfoNewDivaTextGroup', 'http://HOSTURL/textPartSvGroup',
                    'http://HOSTURL/textPartEnGroup']


def test_find_top_level_children(record_node):
    # Add top-level ids
    ET.SubElement(record_node.xml_root.find(".//recordInfo"), "metadataId")
    urls = find_top_level_children(record_node.xml_root)
    assert isinstance(urls, list)


# XML Transformations
def test_normalize_regex_patterns(record_node):
    updated = normalize_regex_patterns(record_node.xml_root)
    regex_text = record_node.xml_root.find(".//regEx").text
    assert updated
    assert regex_text == ".+"


def test_normalize_child_reference_repeat(record_node):
    updated = normalize_child_reference_repeat(record_node.xml_root)
    child = record_node.xml_root.find(".//childReference")
    assert updated
    assert child.find("repeatMin").text == "0"
    assert child.find("repeatMax").text == "X"


def test_update_child_references_multiple(record_node):
    id_mapping = {
        "metadataGroup": "XYZ_metadataGroup",
        "coraTextGroup": "XYZ_coraTextGroup",
        "textPartEnGroup": "XYZ_textPartEnGroup",
    }

    update_child_references(record_node.xml_root, id_mapping)
    after = [el.text.strip() for el in record_node.xml_root.findall(".//linkedRecordId")]

    for old, new in id_mapping.items():
        assert new in after
        assert old not in after


def test_update_record_id_in_xml(record_node):
    update_record_id_in_xml(record_node.xml_root, "XYZ_999")
    assert record_node.xml_root.find(".//recordInfo/id").text == "XYZ_999"


def test_remove_action_links(record_node):
    remove_action_links(record_node.xml_root)
    urls = record_node.xml_root.findall(".//actionLinks")
    assert not urls


def test_clean_and_unwrap_xml(record_node):
    content = clean_and_unwrap_xml(record_node.xml_root)
    assert content.tag == "metadata"
    remove_unwanted_elements(content)
    for tag in ["type", "createdBy", "tsCreated", "updated"]:
        assert content.find(tag) is None


def test_to_xml_bytes(record_node):
    xml_bytes = to_xml_bytes(record_node.xml_root)
    assert isinstance(xml_bytes, bytes)
    assert xml_bytes.startswith(b"<?xml")


# Node processing utilities
def test_create_new_id_and_update_mapping(record_node):
    id_mapping = {}
    new_id = create_new_id_and_update_mapping(id_mapping, record_node, "123")
    assert new_id == "XYZ_123"
    assert id_mapping["123"] == "XYZ_123"
    assert record_node.new_record_id == "XYZ_123"


def test_skip_if_already_processed(record_node):
    id_mapping = {"divaTextNewGroup": "XYZ_divaTextNewGroup"}
    skipped = skip_if_already_processed(record_node, id_mapping)
    assert skipped
    assert record_node.new_record_id == "XYZ_divaTextNewGroup"


# Graph processing
def test_link_parent_child_relationship(record_node):
    child_node = RecordNode("child1", "type1", "http://child1", record_node.xml_root)
    record_node.child_urls = ["http://child1"]
    visited = {
        "http://parent": record_node,
        "http://child1": child_node
    }
    link_parent_child_relationship(visited)
    assert child_node.parents == [record_node]
    assert record_node.children == [child_node]


# Graph bottom-up processing with mocks
def test_process_graph_with_complex_relationships(monkeypatch):
    '''

    A      B
   / \    /
  C   D__/
   \ /  /
    E__/

    '''
    # Create nodes
    node_A = RecordNode("A", "typeA", "urlA", ET.Element("rootA"))
    node_B = RecordNode("B", "typeB", "urlB", ET.Element("rootB"))
    node_C = RecordNode("C", "typeC", "urlC", ET.Element("rootC"))
    node_D = RecordNode("D", "typeD", "urlD", ET.Element("rootD"))
    node_E = RecordNode("E", "typeE", "urlE", ET.Element("rootE"))

    # Define children relationships
    node_A.children = [node_C, node_D]
    node_B.children = [node_D, node_E]
    node_C.children = [node_E]
    node_D.children = [node_E]
    node_E.children = []  # leaf

    # Define parents relationships
    node_C.parents = [node_A]
    node_D.parents = [node_A, node_B]
    node_E.parents = [node_C, node_D, node_B]

    # Build graph
    graph = {
        "urlA": node_A,
        "urlB": node_B,
        "urlC": node_C,
        "urlD": node_D,
        "urlE": node_E
    }

    id_mapping = {}

    processed_order = []

    def fake_process_node(id_mapping, node):
        processed_order.append(node.record_id)
        return True

    monkeypatch.setattr("scripts.create_new_validationTypes.process_node", fake_process_node)

    process_graph_bottom_up_and_store(graph, id_mapping)

    # Check order of processing
    assert processed_order[0] == "E"
    assert processed_order.index("D") > processed_order.index("E")
    assert processed_order.index("C") > processed_order.index("E")
    assert processed_order[-1] in {"A", "B"}
    assert processed_order[-2] in {"A", "B"}
    assert set(processed_order) == {"A", "B", "C", "D", "E"}
