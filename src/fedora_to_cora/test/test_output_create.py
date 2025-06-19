from common.test.helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.output_create import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml


def test_creates_ouput():
    fedora_xml = read_source_xml("data/fedora_xml/1681782_varldskulturmuserna.xml")

    result = transform_to_cora_output(fedora_xml)

    expected_xml = """
    <output>
        <recordInfo>
            <validationType>publication_edited-book</validationType>
            <dataDivider>divaData</dataDivider>
            <permissionUnit>
            <linkedRecordType>permissionUnit</linkedRecordType>
            <linkedRecordId>varldskulturmuseerna</linkedRecordId>
            </permissionUnit>
            <visibility>published</visibility>
            <oldId>diva2:1681782</oldId>
        </recordInfo>
        <genre type="contentType">ref</genre>
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
        </titleInfo>
        <subject lang="eng">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
    </output>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
