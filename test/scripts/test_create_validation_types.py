import xml.etree.ElementTree as ET
from collections import deque

import pytest

import scripts.create_new_validationTypes as Script
from scripts.create_new_validationTypes import BASE_URL


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
    return Script.RecordNode("divaTextNewGroup", "validationType", "http://example.com/record/divaTextNewGroup", root)


def create_mock_top_level_child(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")

    metadata_id = ET.SubElement(record_info, "metadataId")
    action_links = ET.SubElement(metadata_id, "actionLinks")
    read = ET.SubElement(action_links, "read")
    url = ET.SubElement(read, "url")
    url.text = "http://HOSTURL/someTopLevelChild"


# XML Parsing & Node Tests
def test_create_validation_types(monkeypatch):
    global_node_map = {}
    Script.BASE_URL = "http://baseUrl/"

    def fake_build_node_map_from_child_references(root_url, node_map):
        nonlocal  global_node_map
        global_node_map[root_url] = {"record_id": "some_id",}

    def fake_process_graph_bottom_up_and_store(node_map, id_map):
        pass

    def fake_check_for_unprocessed_nodes(node_map, processed):
        pass

    monkeypatch.setattr(Script, "build_node_map_from_child_references", fake_build_node_map_from_child_references)
    monkeypatch.setattr(Script, "process_graph_bottom_up_and_store", fake_process_graph_bottom_up_and_store)
    monkeypatch.setattr(Script, "check_for_unprocessed_nodes", fake_check_for_unprocessed_nodes)

    Script.create_new_validation_types(["someValidationType"])
    assert "http://baseUrl/validationType/someValidationType" in global_node_map
    assert len(global_node_map) == 1


def test_build_node_map_from_child_references_root_url_already_in_map(record_node):
    global_node_map = {"root_url": record_node}

    Script.build_node_map_from_child_references("root_url", global_node_map)
    assert len(global_node_map) == 1


def test_build_node_map_from_child_references_new_url_added(record_node, monkeypatch):
    global_node_map = {}

    def fake_process_queue(queue, root_url, node_map):
        node_map[root_url] = record_node

    monkeypatch.setattr(Script, "process_queue_and_collect_nodes", fake_process_queue)

    Script.build_node_map_from_child_references("http://root_url", global_node_map)
    assert len(global_node_map) == 1
    assert "http://root_url" in global_node_map


def test_process_queue_already_in_node_map(record_node, monkeypatch):
    queue = deque(["some_url"])
    global_node_map = {"some_url": record_node}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return "<xml></xml>"

    monkeypatch.setattr(Script, "fetch_xml_from_api", fake_fetch)
    Script.process_queue_and_collect_nodes(queue, "http://root_url", global_node_map)
    assert called == False


def test_process_queue_and_add_note_to_map(sample_xml, monkeypatch):
    queue = deque(["http://HOSTURL/recordInfoNewDivaTextGroup",
                   "http://HOSTURL/textPartEnGroup",
                   "http://HOSTURL/textPartSvGroup"])
    global_node_map = {}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return sample_xml

    monkeypatch.setattr(Script, "fetch_xml_from_api", fake_fetch)
    Script.process_queue_and_collect_nodes(queue, "http://root_url", global_node_map)
    assert called == True
    assert global_node_map["http://HOSTURL/recordInfoNewDivaTextGroup"].record_id == "divaTextNewGroup"
    assert global_node_map["http://HOSTURL/textPartEnGroup"].record_id == "divaTextNewGroup"
    assert global_node_map["http://HOSTURL/textPartSvGroup"].record_id == "divaTextNewGroup"


def test_process_and_possibly_save_not_saved_due_to_not_updated(record_node, monkeypatch):
    monkeypatch.setattr(Script, "skip_if_already_processed", lambda node, mapping: False)
    monkeypatch.setattr(Script, "normalize_regex_patterns", lambda node: False)
    monkeypatch.setattr(Script, "normalize_child_reference_repeat", lambda node: False)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is False


def test_process_and_possibly_save_not_saved_due_to_already_processed(record_node, monkeypatch):
    def fake_skip_if_already_processed(node, mapping):
        return True

    monkeypatch.setattr("scripts.create_new_validationTypes.skip_if_already_processed", fake_skip_if_already_processed)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is False


def test_process_and_possibly_save(record_node, monkeypatch):
    saved_nodes = []

    def fake_prepare_and_try_to_save_record(node):
        saved_nodes.append(node.record_id)
        return True

    monkeypatch.setattr("scripts.create_new_validationTypes.prepare_and_try_to_save_record",
                        fake_prepare_and_try_to_save_record)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is True
    assert "divaTextNewGroup" in saved_nodes


def test_process_and_possibly_save_not_saved(record_node, monkeypatch):
    def fake_prepare_and_try_to_save_record(node):
        return False

    monkeypatch.setattr("scripts.create_new_validationTypes.prepare_and_try_to_save_record",
                        fake_prepare_and_try_to_save_record)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is False


def test_prepare_and_try_to_save_record(record_node):
    Script.prepare_and_try_to_save_record(record_node)
    assert record_node.record_id == "divaTextNewGroup"
    assert record_node.record_type == "validationType"
    assert record_node.url == "http://example.com/record/divaTextNewGroup"
    assert isinstance(record_node.xml_content, ET.Element)
    assert record_node.new_record_id is None


def test_parse_record_from_xml(sample_xml):
    node = Script.parse_record_from_xml(sample_xml, "http://url")
    assert node.record_id == "divaTextNewGroup"
    assert node.record_type == "metadata"
    assert node.url == "http://url"
    assert isinstance(node.xml_content, ET.Element)


def test_find_child_urls(record_node):
    urls = Script.find_child_urls(record_node.xml_content)
    assert urls == ['http://HOSTURL/recordInfoNewDivaTextGroup', 'http://HOSTURL/textPartSvGroup',
                    'http://HOSTURL/textPartEnGroup']


def test_find_top_level_children(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")

    metadata_id = ET.SubElement(record_info, "metadataId")
    action_links = ET.SubElement(metadata_id, "actionLinks")
    read = ET.SubElement(action_links, "read")
    url = ET.SubElement(read, "url")
    url.text = "http://HOSTURL/someTopLevelChild"

    urls = Script.find_top_level_children(record_node.xml_content)

    assert isinstance(urls, list)
    assert urls == ["http://HOSTURL/someTopLevelChild"]


# XML Transformations
def test_normalize_regex_patterns(record_node):
    updated = Script.normalize_regex_patterns(record_node.xml_content)
    regex_text = record_node.xml_content.find(".//regEx").text
    assert updated
    assert regex_text == ".+"


def test_normalize_child_reference_repeat(record_node):
    updated = Script.normalize_child_reference_repeat(record_node.xml_content)
    child = record_node.xml_content.find(".//childReference")
    assert updated
    assert child.find("repeatMin").text == "0"
    assert child.find("repeatMax").text == "X"


def test_update_child_references_multiple(record_node):
    id_mapping = {
        "metadataGroup": "XYZ_metadataGroup",
        "coraTextGroup": "XYZ_coraTextGroup",
        "textPartEnGroup": "XYZ_textPartEnGroup",
    }

    Script.update_child_references(record_node.xml_content, id_mapping)
    after = [el.text.strip() for el in record_node.xml_content.findall(".//linkedRecordId")]

    for old, new in id_mapping.items():
        assert new in after
        assert old not in after


def test_update_record_id_in_xml(record_node):
    Script.update_record_id_in_xml(record_node.xml_content, "XYZ_999")
    assert record_node.xml_content.find(".//recordInfo/id").text == "XYZ_999"


def test_remove_action_links(record_node):
    Script.remove_action_links(record_node.xml_content)
    urls = record_node.xml_content.findall(".//actionLinks")
    assert not urls


def test_clean_and_unwrap_xml(record_node):
    content = Script.unwrap_and_clean_xml_for_create(record_node.xml_content)
    assert content.tag == "metadata"
    Script.remove_unwanted_elements(content)
    for tag in ["type", "createdBy", "tsCreated", "updated"]:
        assert content.find(tag) is None


def test_to_xml_bytes(record_node):
    xml_bytes = Script.to_xml_bytes(record_node.xml_content)
    assert isinstance(xml_bytes, bytes)
    assert xml_bytes.startswith(b"<?xml")


# Node processing utilities
def test_collect_child_urls(record_node):
    urls = Script.collect_child_urls(record_node, "http://root_url", "http://some_url")
    assert urls == ['http://HOSTURL/recordInfoNewDivaTextGroup', 'http://HOSTURL/textPartSvGroup',
                    'http://HOSTURL/textPartEnGroup']


def test_collect_top_level_children(record_node):
    create_mock_top_level_child(record_node)

    urls = Script.collect_child_urls(record_node, "http://root_url", "http://root_url")

    assert isinstance(urls, list)
    assert urls == ["http://HOSTURL/someTopLevelChild"]


def test_check_for_unprocessed_nodes_updates_total_errors(monkeypatch):
    Script.TOTAL_ERRORS.clear()
    global_node_map = {"url1": object(), "url2": object()}
    processed = {"url1"}

    Script.check_for_unprocessed_nodes(global_node_map, processed)
    assert any("url2" in err for err in Script.TOTAL_ERRORS)
    assert not any("url1" in err for err in Script.TOTAL_ERRORS)


def test_check_for_unprocessed_nodes_no_unprocessed(monkeypatch):
    Script.TOTAL_ERRORS.clear()
    global_node_map = {"url1": object()}
    processed = {"url1"}

    Script.check_for_unprocessed_nodes(global_node_map, processed)
    assert Script.TOTAL_ERRORS == []


def test_create_new_id_and_update_mapping(record_node):
    id_mapping = {}
    new_id = Script.create_new_id_and_update_mapping(id_mapping, record_node, "123")
    assert new_id == "XYZ_123"
    assert id_mapping["123"] == "XYZ_123"
    assert record_node.new_record_id == "XYZ_123"


def test_skip_if_already_processed(record_node):
    id_mapping = {"divaTextNewGroup": "apa"}
    skipped = Script.skip_if_already_processed(record_node, id_mapping)
    assert skipped
    assert record_node.new_record_id == "apa"


def test_skip_if_already_processed_false(record_node):
    id_mapping = {"NotProcessedGroup": "apa"}
    skipped = Script.skip_if_already_processed(record_node, id_mapping)
    assert not skipped


def test_link_parent_child_relationship(record_node):
    child_node = Script.RecordNode("child_node", "someType", "http://child_node", record_node.xml_content)
    record_node.child_urls = ["http://child_node"]
    visited = {
        "http://parent_node": record_node,
        "http://child_node": child_node
    }
    Script.link_parent_child_relationship(visited)
    assert child_node.parents == [record_node]
    assert record_node.children == [child_node]


def test_process_node_success(monkeypatch, record_node):
    Script.TOTAL_PROCESSED_RECORDS = 0
    Script.TOTAL_UPDATES = 0
    Script.TOTAL_ERRORS.clear()

    monkeypatch.setattr(Script, "process_and_possibly_save", lambda node, mapping: True)
    Script.process_node({}, record_node)
    assert Script.TOTAL_PROCESSED_RECORDS == 1
    assert Script.TOTAL_UPDATES == 1
    assert Script.TOTAL_ERRORS == []


def test_process_node_failure(monkeypatch, record_node):
    Script.TOTAL_PROCESSED_RECORDS = 0
    Script.TOTAL_UPDATES = 0
    Script.TOTAL_ERRORS.clear()

    def throw_exception(node, mapping):
        raise ValueError("fail to save")

    monkeypatch.setattr(Script, "process_and_possibly_save", throw_exception)
    Script.process_node({}, record_node)
    assert Script.TOTAL_PROCESSED_RECORDS == 1
    assert Script.TOTAL_UPDATES == 0
    assert len(Script.TOTAL_ERRORS) == 1
    assert "Error processing divaTextNewGroup: fail to save" in Script.TOTAL_ERRORS[0]


# Node map bottom-up processing with mocks
def test_process_graph_with_relationships(monkeypatch):
    #    '''
    #
    #    A     B
    #   / \    |
    #  C   D   |
    #   \ /   /
    #    E___/
    #
    #    '''
    # Create nodes
    node_A = Script.RecordNode("A", "typeA", "urlA", ET.Element("xmlrootA"))
    node_B = Script.RecordNode("B", "typeB", "urlB", ET.Element("nodeB"))
    node_C = Script.RecordNode("C", "typeC", "urlC", ET.Element("nodeC"))
    node_D = Script.RecordNode("D", "typeD", "urlD", ET.Element("nodeD"))
    node_E = Script.RecordNode("E", "typeE", "urlE", ET.Element("nodeE"))

    # Define children relationships
    node_A.children = [node_C, node_D]
    node_B.children = [node_E]
    node_C.children = [node_E]
    node_D.children = [node_E]
    node_E.children = []  # leaf

    # Define parents relationships
    node_C.parents = [node_A]
    node_D.parents = [node_A]
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

    Script.process_node_map_bottom_up_and_store(graph, id_mapping)

    # Check order of processing
    assert processed_order[0] == "E"
    assert processed_order.index("D") > processed_order.index("E")
    assert processed_order.index("C") > processed_order.index("E")
    assert processed_order[-1] in {"A", "B"}
    assert processed_order[-2] in {"A", "B"}
    assert set(processed_order) == {"A", "B", "C", "D", "E"}
