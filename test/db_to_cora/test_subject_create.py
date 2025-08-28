import xml.etree.ElementTree as ET
from db_to_cora.subject_transform import transform_subject
from common.test_helper import assert_equal_for_xml_and_xml_string

def test_required_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <name_swe>En test</name_swe>
        </DATA_RECORD>      
        """
    )

    result = transform_subject(source_record)

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    
def test_complete_without_links_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <end_date>2025-08-20</end_date>
            <name_swe>En test</name_swe>
            <name_eng>en testpost</name_eng>
        </DATA_RECORD>  
        """
    )

    result = transform_subject(source_record)
    secondResultSameRun = transform_subject(source_record)

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
            <variant lang="eng">
                <topic>en testpost</topic>
            </variant>
            <endDate>
                <year>2025</year>
                <month>08</month>
                <day>20</day>
            </endDate>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    assert_equal_for_xml_and_xml_string(secondResultSameRun, expected_xml)
    
    
def test_complete_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <end_date>2025-08-20</end_date>
            <name_swe>En test</name_swe>
            <name_eng>en testpost</name_eng>
            <broader_id>1234</broader_id>
            <earlier_id>9876</earlier_id>
        </DATA_RECORD>  
        """
    )

    result = transform_subject(source_record)

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
            <variant lang="eng">
                <topic>en testpost</topic>
            </variant>
            <endDate>
                <year>2025</year>
                <month>08</month>
                <day>20</day>
            </endDate>
            <related repeatId="0" type="broader">
                <topic>
                    <linkedRecordType>diva-subject</linkedRecordType>
                    <linkedRecordId>1234</linkedRecordId>
                </topic>
            </related>
            <related repeatId="1" type="earlier">
                <topic>
                    <linkedRecordType>diva-subject</linkedRecordType>
                    <linkedRecordId>9876</linkedRecordId>
                </topic>
            </related>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    
    