import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import requests
from jedi.common import monkeypatch

import scripts.delete_validationTypes_for_recordType as Script


@pytest.fixture(autouse=True)
def mock_ctx():
    Script.CTX = MagicMock()
    Script.CTX.get_base_url.return_value = "http://baseUrl/"
    Script.CTX.get_auth_token.return_value = "authToken"
    yield Script.CTX
    del Script.CTX


@pytest.fixture(autouse=True)
def reset_global_data():
    Script.GLOBAL_RECORD_INFO_CHILDREN.clear()
    Script.TOTAL_ERRORS.clear()
    Script.TOTAL_PROCESSED_RECORDS = 0
    Script.TOTAL_RECORD_DELETIONS = 0
    Script.TOTAL_PRESENTATION_DELETIONS = 0
    Script.TOTAL_FETCHED = 0


@pytest.fixture()
def create_node_tree():
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
    node_B = Script.RecordNode("B", "typeB", "urlB", ET.Element("xmlrootB"))
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

    return {"A": node_A, "B": node_B, "C": node_C, "D": node_D, "E": node_E}


class MockResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}: {self.text}")


@pytest.fixture(autouse=True)
def mock_requests(monkeypatch, sample_xml, validation_type_search_result_xml):
    def fake_get(url, *args, **kwargs):
        if "validationTypeSearch" in url:
            return MockResponse(validation_type_search_result_xml, 200)

        else:
            return MockResponse(sample_xml, 200)

    def fake_delete(url, data=None, *args, **kwargs):
        return MockResponse(f"<created url='{url}'>{data}</created>", 201)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "delete", fake_delete)


@pytest.fixture
def presentation_search_result_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<recordList>
    <record>
    <presentation>
        <recordInfo>
            <id>__XYZ_pres1</id>
            <title>aok</title>
        </recordInfo>
    </presentation>
    <presentation>
        <recordInfo>
            <id>__XYZ_pres2</id>
            <title>aok2 Type 2</title>
        </recordInfo>
    </presentation>
    </record>
</recordList>
"""


@pytest.fixture
def validation_type_search_result_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
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
    return Script.RecordNode("divaTextNewGroup", "validationType", "http://HOSTURL/record/divaTextNewGroup", root)


def create_mock_top_level_child(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")
    name_in_data = record_node.xml_content.find(".//nameInData")
    name_in_data.text = "recordInfo"

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

    def fake_collect_nodes_from_root(root_url, node_map):
        node_map[root_url] = record_node

    monkeypatch.setattr(Script, "collect_nodes_from_root", fake_collect_nodes_from_root)

    Script.build_node_map_from_child_references("http://root_url", global_node_map)
    assert len(global_node_map) == 1
    assert "http://root_url" in global_node_map


def test_process_queue_already_in_node_map(record_node, monkeypatch):
    global_node_map = {"http://root_url": record_node}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return "<xml></xml>"

    monkeypatch.setattr(Script, "fetch_record_as_xml", fake_fetch)
    Script.collect_nodes_from_root("http://root_url", global_node_map)
    assert called == False


def test_process_queue_and_add_note_to_map(sample_xml, monkeypatch):
    global_node_map = {}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return sample_xml

    def fake_collect_child_urls(node, root_url, url):
        return ["http://child_url", "http://another_child_url"]

    monkeypatch.setattr(Script, "fetch_record_as_xml", fake_fetch)
    monkeypatch.setattr(Script, "collect_child_urls", fake_collect_child_urls)

    Script.collect_nodes_from_root("http://root_url", global_node_map)
    assert called == True
    assert global_node_map["http://root_url"].record_id == "divaTextNewGroup"


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
    global_node_map = {"url1": object(), "url2": object()}
    processed = {"url1"}

    Script.check_for_unprocessed_nodes(global_node_map, processed)
    assert any("url2" in err for err in Script.TOTAL_ERRORS)
    assert not any("url1" in err for err in Script.TOTAL_ERRORS)


def test_check_for_unprocessed_nodes_no_unprocessed(monkeypatch):
    global_node_map = {"url1": object()}
    processed = {"url1"}

    Script.check_for_unprocessed_nodes(global_node_map, processed)
    assert Script.TOTAL_ERRORS == []


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


def test_process_graph_with_relationships(monkeypatch, create_node_tree):
    node_tree = create_node_tree

    node_map = {
        "urlA": node_tree["A"],
        "urlB": node_tree["B"],
        "urlC": node_tree["C"],
        "urlD": node_tree["D"],
        "urlE": node_tree["E"]
    }

    processed_order = []

    def fake_process_node(node):
        processed_order.append(node.record_id)
        return True

    monkeypatch.setattr("scripts.delete_validationTypes_for_recordType.prepare_url_and_possibly_delete",
                        fake_process_node)

    Script.process_node_map_and_delete_records(node_map)

    # Check order of processing
    assert processed_order[0] == "A"
    assert processed_order[1] == "B"

    assert processed_order.index("D") < processed_order.index("E")
    assert processed_order.index("C") < processed_order.index("E")

    assert processed_order[4] in {"E"}
    assert processed_order[3] in {"D"}
    assert set(processed_order) == {"A", "B", "C", "D", "E"}


def test_get_search_data():
    data = Script.get_search_data("something")
    assert data is not None


def test_get_validation_types_for_record_type():
    results = Script.get_validation_types_for_record_type()
    assert results == ["valType1", "valType2"]


def test_collect_validation_types_from_response(monkeypatch, validation_type_search_result_xml):
    validation_type_search_result = ET.fromstring(validation_type_search_result_xml)
    list_of_types = Script.collect_validation_types_from_response(validation_type_search_result)
    assert list_of_types == ["valType1", "valType2"]


def test_collect_validation_types_from_response_with_blacklisted_types(monkeypatch, validation_type_search_result_xml):
    search_result = ET.fromstring(validation_type_search_result_xml)
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


def test_log_results_no_errors(monkeypatch, mock_ctx):
    Script.TOTAL_ERRORS = []
    Script.log_results()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]

    assert any("No errors reported." in msg for msg in calls)


def test_try_to_delete_record_fail_due_to_bad_prefix(monkeypatch):
    Script.TYPE_PREFIX = "__SOMETHING_"
    success = Script.try_to_delete_record("someUrl")
    assert not success


def test_try_to_delete_record_success(monkeypatch):
    Script.TYPE_PREFIX = "__SOMETHING_"
    def fake_delete(url, data=None, *args, **kwargs):
        return MockResponse("Record deleted", 200)

    monkeypatch.setattr(requests, "delete", fake_delete)
    success = Script.try_to_delete_record("__SOMETHING_someUrl")
    assert success


def test_try_to_delete_record_failed(monkeypatch):
    Script.TYPE_PREFIX = "__SOMETHING_"
    def fake_delete(url, data=None, *args, **kwargs):
        return MockResponse("Record deleted", 405)

    monkeypatch.setattr(requests, "delete", fake_delete)
    success = Script.try_to_delete_record("__SOMETHING_someUrl")
    assert not success


def test_try_to_delete_record_with_exception(monkeypatch):
    Script.TYPE_PREFIX = "__SOMETHING_"
    def fake_delete(url, data=None, *args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(requests, "delete", fake_delete)
    success = Script.try_to_delete_record("__SOMETHING_someUrl")
    assert not success


def test_try_to_delete_presentations_dry_run(monkeypatch, presentation_search_result_xml, mock_ctx):
    Script.DRY_RUN = True
    def fake_collect_presentations_from_response(response):
        return {"hej", "san"}

    monkeypatch.setattr(Script, "collect_presentations_from_response", fake_collect_presentations_from_response)

    Script.try_to_delete_presentations()
    assert Script.TOTAL_PRESENTATION_DELETIONS == 2


def test_try_to_delete_presentations(monkeypatch, presentation_search_result_xml, mock_ctx):
    Script.DRY_RUN = False
    def fake_collect_presentations_from_response(response):
        return {"hej", "san"}

    def fake_delete(url):
        return True

    monkeypatch.setattr(Script, "collect_presentations_from_response", fake_collect_presentations_from_response)
    monkeypatch.setattr(Script, "try_to_delete_record", fake_delete)

    Script.try_to_delete_presentations()
    assert Script.TOTAL_PRESENTATION_DELETIONS == 2


def test_try_to_delete_presentations_fail_giveup_to_many_retries(monkeypatch, presentation_search_result_xml, mock_ctx):
    Script.DRY_RUN = False
    def fake_collect_presentations_from_response(response):
        return {"hej", "san"}

    def fake_delete(url):
        return False

    monkeypatch.setattr(Script, "collect_presentations_from_response", fake_collect_presentations_from_response)
    monkeypatch.setattr(Script, "try_to_delete_record", fake_delete)

    Script.try_to_delete_presentations()
    assert Script.TOTAL_PRESENTATION_DELETIONS == 0
    assert "Failed to delete hej after 5 retries!" in Script.TOTAL_ERRORS
    assert "Failed to delete san after 5 retries!" in Script.TOTAL_ERRORS


def test_try_to_delete_presentations_fail_with_retry_and_success(monkeypatch, presentation_search_result_xml, mock_ctx):
    Script.DRY_RUN = False
    def fake_collect_presentations_from_response(response):
        return {"hej", "san"}

    call_count = 0
    def fake_delete(url):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return False
        else:
            return True

    monkeypatch.setattr(Script, "collect_presentations_from_response", fake_collect_presentations_from_response)
    monkeypatch.setattr(Script, "try_to_delete_record", fake_delete)

    Script.try_to_delete_presentations()
    assert Script.TOTAL_PRESENTATION_DELETIONS == 2
    assert not Script.TOTAL_ERRORS


def test_prepare_url_and_possibly_delete_dry_run(record_node):
    Script.TYPE_PREFIX = "__hej_"
    Script.DRY_RUN = True
    record_node.record_id = "__hej_san"
    assert Script.prepare_url_and_possibly_delete(record_node)


def test_prepare_url_and_possibly_delete(record_node):
    Script.TYPE_PREFIX = "__hej_"
    Script.DRY_RUN = False
    record_node.record_id = "__hej_san"
    assert Script.prepare_url_and_possibly_delete(record_node)


def test_prepare_url_and_possibly_delete_bad_prefix(record_node):
    Script.TYPE_PREFIX = "__helloes_"
    Script.DRY_RUN = False
    record_node.record_id = "__ohnoes_san"
    assert not Script.prepare_url_and_possibly_delete(record_node)


def test_collect_presentations_from_response(presentation_search_result_xml):
    Script.TYPE_PREFIX = "__XYZ_"
    presentation_search_result = ET.fromstring(presentation_search_result_xml)
    list_of_types = Script.collect_presentations_from_response(presentation_search_result)
    assert list_of_types == {"http://baseUrl/presentation/__XYZ_pres1", "http://baseUrl/presentation/__XYZ_pres2"}


def test_delete_validation_types_for_record_type(monkeypatch, mock_ctx):
    monkeypatch.setattr(Script, "get_validation_types_for_record_type", lambda: ["valType1", "valType2"])
    monkeypatch.setattr(Script, "build_node_map_from_child_references", lambda url, mapping: mapping.update(
        {url: Script.RecordNode("id", "type", url, ET.Element("xml"))}))
    monkeypatch.setattr(Script, "process_node_map_and_delete_records", lambda id_map: {})
    monkeypatch.setattr(Script, "check_for_unprocessed_nodes", lambda mapping, processed: None)

    Script.delete_records_with_prefix()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]
    assert any("=== Script finished ===" in msg for msg in calls)


def test_delete_validation_types_for_record_type_no_nodemap(monkeypatch, mock_ctx):
    Script.GLOBAL_NODE_MAP = {}
    monkeypatch.setattr(Script, "get_validation_types_for_record_type", lambda: [])

    Script.delete_records_with_prefix()

    calls = [call.args[0] for call in mock_ctx.log.mock_calls]
    assert any("No presentations found to delete..." in msg for msg in calls)
    assert any("No validationTypes found to delete..." in msg for msg in calls)
    assert any("There is nothing to delete..." in msg for msg in calls)
    assert any("=== Script finished ===" in msg for msg in calls)


def test_main(monkeypatch, mock_ctx):
    fake_args = SimpleNamespace(
        system="testSystem",
        login_id="user",
        app_token="token",
        workers=1,
        prefix="__XYZ_",
        recordtype="diva-output",
        datadivider="diva",
        apply=False
    )

    monkeypatch.setattr(Script, "create_argument_parser",
                        lambda **kwargs: SimpleNamespace(parse_args=lambda: fake_args))
    monkeypatch.setattr(Script, "CoraContext", lambda **kwargs: mock_ctx)

    Script.main()

    assert Script.CTX is mock_ctx
