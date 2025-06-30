import xml.etree.ElementTree as ET
from db_to_cora.publisher_transform import transform_publisher
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_element_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <name>Some name</name>
        </DATA_RECORD>       
        """
    )

    result = transform_publisher(source_record)

    expected_xml = """
    <publisher>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-publisher</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <name type="corporate">
            <namePart>Some name</namePart>
        </name>
    </publisher>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
