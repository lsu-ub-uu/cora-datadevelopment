import xml.etree.ElementTree as ET
from db_to_cora.funder_transform import transform_funder
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_element_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <name_swe>Ett namn</name_swe>
        </DATA_RECORD>       
        """
    )
    
    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <authority lang="swe">
            <name type="corporate">
                <namePart>Ett namn</namePart>
            </name>
        </authority>
    </funder>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    
    
def test_element_variant_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <name_swe>Ett namn</name_swe>
            <name_eng>Some name</name_eng>      
        </DATA_RECORD>       
        """
    )
    
    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <authority lang="swe">
            <name type="corporate">
                <namePart>Ett namn</namePart>
            </name>
        </authority>
        <variant lang="eng">
            <name type="corporate">
                <namePart>Some name</namePart>
            </name>
        </variant>
    </funder>
    """
    
    assert_equal_for_xml_and_xml_string(result, expected_xml)
    
    
    
    
