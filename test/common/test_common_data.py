import xml.etree.ElementTree as ET

from common import common_data
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_record_link():
    name_in_data = "someNameInData"
    record_type = "someType"
    record_id = "someId"

    link = common_data.create_record_link(name_in_data, record_type, record_id)

    expected_xml = """
                    <someNameInData> 
                        <linkedRecordType>someType</linkedRecordType>
                        <linkedRecordId>someId</linkedRecordId>
                    </someNameInData>
                    """

    assert_equal_for_xml_and_xml_string(link, expected_xml)


def test_create_record_link_using_name_type_id():
    name_in_data = "someNameInData"
    record_type = "someRecordType"
    record_id = "someRecordId"

    link = common_data.create_record_link(name_in_data, record_type, record_id)

    expected_xml = """<someNameInData>
                        <linkedRecordType>someRecordType</linkedRecordType>
                        <linkedRecordId>someRecordId</linkedRecordId>
                    </someNameInData>
                    """

    assert_equal_for_xml_and_xml_string(link, expected_xml)
