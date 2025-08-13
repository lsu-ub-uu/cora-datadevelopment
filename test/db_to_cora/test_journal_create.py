import xml.etree.ElementTree as ET
from db_to_cora.journal_transform import transform_journal
from common.test_helper import assert_equal_for_xml_and_xml_string

def test_element_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <title>some title</title>
        </DATA_RECORD>       
        """
    )

    result = transform_journal(source_record)

    expected_xml = """
    <journal>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-journal</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <titleInfo>
            <title>some title</title>
        </titleInfo>
    </journal>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)