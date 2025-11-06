import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

import pytest
import requests

from common import validation_type_utils as common_utils
from cora.context import CoraContext


@pytest.fixture
def init_utils():
    ctx: CoraContext = MagicMock()
    ctx.get_base_url.return_value = "http://baseUrl/"
    ctx.get_auth_token.return_value = "authToken"
    common_utils.init(ctx, "__test_prefix_", "test_type", ["black_listed"])
    yield


@pytest.fixture(autouse=True)
def reset_global_data():
    common_utils._ctx = None
    common_utils._type_prefix = ""
    common_utils._record_type = ""
    common_utils._black_list = []


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
    node_A = common_utils.RecordNode("A", "typeA", "urlA", ET.Element("xmlrootA"))
    node_B = common_utils.RecordNode("B", "typeB", "urlB", ET.Element("xmlrootB"))
    node_C = common_utils.RecordNode("C", "typeC", "urlC", ET.Element("nodeC"))
    node_D = common_utils.RecordNode("D", "typeD", "urlD", ET.Element("nodeD"))
    node_E = common_utils.RecordNode("E", "typeE", "urlE", ET.Element("nodeE"))

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
def mock_requests(monkeypatch, sample_xml, validation_type_search_result_xml, presentation_search_result_xml):
    def fake_get(url, *args, **kwargs):
        if "validationTypeSearch" in url:
            return MockResponse(validation_type_search_result_xml, 200)
        elif "presentationSearch" in url:
            return MockResponse(presentation_search_result_xml, 200)
        else:
            return MockResponse(sample_xml, 200)

    def fake_post(url, data=None, *args, **kwargs):
        if "return400" in url:
            return MockResponse("failed to post", 400)
        elif "throw_exception" in url:
            raise requests.HTTPError("threw exception")
        else:
            return MockResponse(f"<created url='{url}'>{data}</created>", 201)

    def fake_delete(url: str, data=None, *args, **kwargs):
        if url.endswith("throw_exception"):
            raise requests.HTTPError("some exception")
        elif url.endswith("not200"):
            return MockResponse("failed to delete", 400)
        else:
            return MockResponse("deleted post", 200)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)
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
        <validationType>
        <recordInfo>
            <id>black_listed</id>
            <title>Validation Type 3</title>
        </recordInfo>
    </validationType>
    </record>
</recordList>
"""


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def record_node(sample_xml):
    root = ET.fromstring(sample_xml)
    return common_utils.RecordNode("divaTextNewGroup", "validationType", "http://HOSTURL/record/divaTextNewGroup", root)


@pytest.fixture(scope="function")
def another_record_node(sample_xml):
    root = ET.fromstring(sample_xml)
    return common_utils.RecordNode("someOtherGroup", "metadata", "http://HOSTURL/record/metadata/someOtherGroup", root)


@pytest.fixture()
def mock_top_level(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")
    name_in_data = record_node.xml_content.find(".//nameInData")
    name_in_data.text = "recordInfo"

    metadata_id = ET.SubElement(record_info, "newMetadataId")
    action_links = ET.SubElement(metadata_id, "actionLinks")
    read = ET.SubElement(action_links, "read")
    url = ET.SubElement(read, "url")
    url.text = "http://HOSTURL/newGroupChild"

    metadata_id = ET.SubElement(record_info, "metadataId")
    action_links = ET.SubElement(metadata_id, "actionLinks")
    read = ET.SubElement(action_links, "read")
    url = ET.SubElement(read, "url")
    url.text = "http://HOSTURL/updateGroupChild"
