import xml.etree.ElementTree as ET

from common import common_data
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_record_link():
    name_in_data = "someNameInData"
    record_type = "someType"
    record_id = "someId"

    link = common_data.create_record_link_using_name_type_id(
        name_in_data, record_type, record_id
    )

    expected_xml = """
                    <someNameInData> 
                        <linkedRecordType>someType</linkedRecordType>
                        <linkedRecordId>someId</linkedRecordId>
                    </someNameInData>
                    """

    assert_equal_for_xml_and_xml_string(link, expected_xml)


def test_get_oldId():
    source_record = ET.fromstring(
        """
        <record>
            <old_id>12345</old_id>
        </record>
        """
    )

    old_id = common_data.get_oldId(source_record)

    assert old_id == "12345"


def test_endDate_yearMonthDay():
    year = "2023"
    month = "10"
    day = "05"
    root_element = ET.Element("root")

    common_data.endDate_yearMonthDay(year, month, day, root_element)

    expected_xml = """
                    <root>
                        <year>2023</year>
                        <month>10</month>
                        <day>05</day>
                    </root>
                    """

    assert_equal_for_xml_and_xml_string(root_element, expected_xml)


def test_record_info_build():
    record_type = "someRecordType"
    permission_unit = "somePermissionUnit"
    data_record = ET.fromstring(
        """
        <record>
        </record>
    """
    )
    new_record_element = ET.Element("newRecord")
    common_data.record_info_build(
        record_type, permission_unit, data_record, new_record_element
    )

    expected_xml = """
                    <newRecord>
                        <recordInfo>
                            <validationType>
                                <linkedRecordType>validationType</linkedRecordType>
                                <linkedRecordId>diva-someRecordType</linkedRecordId>
                            </validationType>
                            <dataDivider>
                                <linkedRecordType>system</linkedRecordType>
                                <linkedRecordId>divaData</linkedRecordId>
                            </dataDivider>
                            <permissionUnit>
                                <linkedRecordType>permissionUnit</linkedRecordType>
                                <linkedRecordId>somePermissionUnit</linkedRecordId>
                            </permissionUnit>
                        </recordInfo>
                    </newRecord>
                    """

    assert_equal_for_xml_and_xml_string(new_record_element, expected_xml)


def test_record_info_build_with_od_id():
    record_type = "someRecordType"
    permission_unit = "somePermissionUnit"
    data_record = ET.fromstring(
        """
        <record>
            <old_id>12345</old_id>
        </record>
    """
    )
    new_record_element = ET.Element("newRecord")
    common_data.record_info_build(
        record_type, permission_unit, data_record, new_record_element
    )

    expected_xml = """
                    <newRecord>
                        <recordInfo>
                            <validationType>
                                <linkedRecordType>validationType</linkedRecordType>
                                <linkedRecordId>diva-someRecordType</linkedRecordId>
                            </validationType>
                            <dataDivider>
                                <linkedRecordType>system</linkedRecordType>
                                <linkedRecordId>divaData</linkedRecordId>
                            </dataDivider>
                            <permissionUnit>
                                <linkedRecordType>permissionUnit</linkedRecordType>
                                <linkedRecordId>somePermissionUnit</linkedRecordId>
                            </permissionUnit>
                            <oldId>12345</oldId>
                        </recordInfo>
                    </newRecord>
                    """

    assert_equal_for_xml_and_xml_string(new_record_element, expected_xml)


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


def test_create_record_link_using_name_type_id():
    name_in_data = "someNameInData"
    record_type = "someRecordType"
    record_id = "someRecordId"

    link = common_data.create_record_link_using_name_type_id(
        name_in_data, record_type, record_id
    )

    expected_xml = """<someNameInData>
                        <linkedRecordType>someRecordType</linkedRecordType>
                        <linkedRecordId>someRecordId</linkedRecordId>
                    </someNameInData>
                    """

    assert_equal_for_xml_and_xml_string(link, expected_xml)
   