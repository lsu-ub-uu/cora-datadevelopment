import xml.etree.ElementTree as ET
from collections import deque
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests

import scripts.create_new_validationTypes_for_recordType as Script


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}: {self.text}")


@pytest.fixture(autouse=True)
def mock_ctx():
    Script.CTX = MagicMock()
    Script.CTX.get_base_url.return_value = "http://baseUrl/"
    Script.CTX.get_auth_token.return_value = "authToken"
    yield Script.CTX
    del Script.CTX


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch, sample_xml):
    def fake_get(url, *args, **kwargs):
        if "validationTypeSearch" in url:
            return MockResponse(get_validation_type_search_response_as_xml(), 200)

        else:
            return MockResponse(sample_xml, 200)

    def fake_post(url, data=None, *args, **kwargs):
        return MockResponse(f"<created url='{url}'>{data}</created>", 201)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)


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

    monkeypatch.setattr(Script, "fetch_record_as_xml", fake_fetch)
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

    monkeypatch.setattr(Script, "fetch_record_as_xml", fake_fetch)
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

    monkeypatch.setattr("scripts.create_new_validationTypes_for_recordType.skip_if_already_processed",
                        fake_skip_if_already_processed)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is False


def test_process_and_possibly_save(record_node, monkeypatch):
    saved_nodes = []

    def fake_prepare_and_try_to_save_record(node):
        saved_nodes.append(node.record_id)
        return True

    monkeypatch.setattr("scripts.create_new_validationTypes_for_recordType.prepare_and_try_to_save_record",
                        fake_prepare_and_try_to_save_record)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is True
    assert "divaTextNewGroup" in saved_nodes


def test_process_and_possibly_save_not_saved(record_node, monkeypatch):
    def fake_prepare_and_try_to_save_record(node):
        return False

    monkeypatch.setattr("scripts.create_new_validationTypes_for_recordType.prepare_and_try_to_save_record",
                        fake_prepare_and_try_to_save_record)

    result = Script.process_and_possibly_save(record_node, {"123": "XYZ_123"})
    assert result is False


def test_prepare_and_try_to_save_record(record_node, monkeypatch):
    Script.prepare_and_try_to_save_record(record_node)

    assert record_node.record_id == "divaTextNewGroup"
    assert record_node.record_type == "validationType"
    assert record_node.url == "http://example.com/record/divaTextNewGroup"
    assert isinstance(record_node.xml_content, ET.Element)


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
    assert new_id == "__XYZ_123"
    assert id_mapping["123"] == "__XYZ_123"
    assert record_node.new_record_id == "__XYZ_123"


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

    monkeypatch.setattr("scripts.create_new_validationTypes_for_recordType.process_node", fake_process_node)

    Script.process_node_map_bottom_up_and_store(graph, id_mapping)

    # Check order of processing
    assert processed_order[0] == "E"
    assert processed_order.index("D") > processed_order.index("E")
    assert processed_order.index("C") > processed_order.index("E")
    assert processed_order[-1] in {"A", "B"}
    assert processed_order[-2] in {"A", "B"}
    assert set(processed_order) == {"A", "B", "C", "D", "E"}


def test_get_search_data():
    data = Script.get_search_data()
    assert data is not None


def test_get_validation_types_for_record_type():
    results = Script.get_validation_types_for_record_type()
    assert results == ["valType1", "valType2"]


def test_collect_validation_types_from_response(monkeypatch):
    sample_response_as_xml = ET.fromstring(get_validation_type_search_response_as_xml())

    list_of_types = Script.collect_validation_types_from_response(sample_response_as_xml)
    assert list_of_types == ["valType1", "valType2"]


def test_collect_validation_types_from_response_with_blacklisted_types(monkeypatch):
    search_result = ET.fromstring(get_validation_type_search_response_as_xml())
    for elem in search_result.iter("id"):
        if elem.text == "valType2":
            elem.text = "diva-output"
            break

    list_of_types = Script.collect_validation_types_from_response(search_result)
    assert len(list_of_types) == 1
    assert list_of_types == ["valType1"]


def test_fetch_record_as_xml(monkeypatch, sample_xml):
    xml = Script.fetch_record_as_xml("http://someurl/record")
    assert sample_xml in xml


def test_try_to_store_record_with_failed_response(monkeypatch, record_node):
    def fake_post(url, data=None, *args, **kwargs):
        return MockResponse("Error occurred", 400)

    monkeypatch.setattr(requests, "post", fake_post)
    success = Script.try_to_store_record(record_node, "someUrl", b"<xml></xml>")
    assert not success


def test_try_to_store_record_with_exception(monkeypatch, record_node):
    def fake_post(url, data=None, *args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(requests, "post", fake_post)
    success = Script.try_to_store_record(record_node, "someUrl", b"<xml></xml>")
    assert not success


def test_log_results(monkeypatch, mock_ctx):
    Script.TOTAL_FETCHED = 10
    Script.TOTAL_PROCESSED_RECORDS = 8
    Script.TOTAL_UPDATES = 5
    Script.TOTAL_ERRORS = ["Error 1", "Error 2"]
    Script.log_results()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]

    assert "Total records fetched:   10" in calls[0]
    assert "Total records processed: 8" in calls[1]
    assert "Total records created:   5" in calls[2]

    assert any("WARNING" in msg for msg in calls)

    assert any("=== Errors reported ===" in msg for msg in calls)
    assert any(" > Error 1" in msg for msg in calls)
    assert any(" > Error 2" in msg for msg in calls)


def test_log_results_no_errors(monkeypatch, mock_ctx):
    Script.TOTAL_ERRORS = []
    Script.log_results()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]

    assert any("No errors reported." in msg for msg in calls)


def test_create_new_validation_types_for_record_type(monkeypatch, mock_ctx):
    monkeypatch.setattr(Script, "get_validation_types_for_record_type", lambda: ["valType1", "valType2"])
    monkeypatch.setattr(Script, "build_node_map_from_child_references", lambda url, mapping: mapping.update(
        {url: Script.RecordNode("id", "type", url, ET.Element("xml"))}))
    monkeypatch.setattr(Script, "process_node_map_bottom_up_and_store", lambda mapping, id_map: {})
    monkeypatch.setattr(Script, "check_for_unprocessed_nodes", lambda mapping, processed: None)

    Script.create_new_validation_types_for_record_type()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]
    assert any("=== Script finished ===" in msg for msg in calls)


def test_main(monkeypatch, mock_ctx):
    fake_args = SimpleNamespace(
        system="testSystem",
        login_id="user",
        app_token="token",
        workers=1
    )

    monkeypatch.setattr(Script, "create_argument_parser",
                        lambda **kwargs: SimpleNamespace(parse_args=lambda: fake_args))
    monkeypatch.setattr(Script, "CoraContext", lambda **kwargs: mock_ctx)

    Script.main()

    assert Script.CTX is mock_ctx


def get_validation_type_search_response_as_xml() -> str:
    sample_response_as_xml = """<?xml version="1.0" encoding="UTF-8"?>
<recordList>
    <record>
    <validationType>
        <recordInfo>
            <id>valType1</id>
            <title>Validation Type 1</title>
        </recordInfo>
    </validationType>
    <validationType>
        <recordInfo>
            <id>valType2</id>
            <title>Validation Type 2</title>
        </recordInfo>
    </validationType>
    </record>
</recordList>
"""
    return sample_response_as_xml
