import xml.etree.ElementTree as ET

from common import common_data
from common.test.helper import assert_equal_for_xml_and_xml_string

def test_create_link():
    name_in_data = "someNameInData" 
    record_type = "someType"
    record_id = "someId"
    
    link = common_data.create_record_link_using_name_type_id(name_in_data, record_type, record_id)
    
    expected_xml = """
                    <someNameInData>
                        <linkedRecordType>someType</linkedRecordType>
                        <linkedRecordId>someId</linkedRecordId>
                    </someNameInData>
                    """
    
    assert_equal_for_xml_and_xml_string(link, expected_xml)
    
def test_create_record_info():
    record_info = common_data.create_record_info_for_record_type("someRecordType")
    
    expected_xml = """
                    <recordInfo>
                        <validationType> 
                            <linkedRecordType>validationType</linkedRecordType>
                            <linkedRecordId>diva-someRecordType</linkedRecordId>
                        </validationType>
                        <dataDivider>
                            <linkedRecordType>system</linkedRecordType>
                            <linkedRecordId>divaData</linkedRecordId>
                        </dataDivider>
                    </recordInfo>
                    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)

