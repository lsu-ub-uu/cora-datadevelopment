import xml.etree.ElementTree as ET
from common.record_info_create import record_info_create
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_record_info_create():
    record_info = record_info_create(
        validation_type_id="someValidationType",
        old_id="12345",
        permission_unit_id="somePermissionUnit",
    )

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
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
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)


def test_record_info_create_without_permission_unit():
    record_info = record_info_create(
        validation_type_id="someValidationType", old_id="12345", permission_unit_id=None
    )

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>12345</oldId>
        </recordInfo>
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)


def test_record_info_create_with_only_validation_type():
    record_info = record_info_create(validation_type_id="someValidationType")

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
        </recordInfo>
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)


def test_record_info_create_with_visibility():
    record_info = record_info_create(
        validation_type_id="someValidationType", visibility="published"
    )

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <visibility>published</visibility>
        </recordInfo>
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)


def test_record_info_create_with_host_record():
    host_record = ET.fromstring(
        "<hostRecord><linkedRecordType>someType</linkedRecordType><linkedRecordId>someId</linkedRecordId></hostRecord>"
    )

    record_info = record_info_create(
        validation_type_id="someValidationType",
        old_id="12345",
        permission_unit_id="somePermissionUnit",
        host_record_link=host_record,
    )

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
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
            <hostRecord>
                <linkedRecordType>someType</linkedRecordType>
                <linkedRecordId>someId</linkedRecordId>
            </hostRecord>
        </recordInfo>
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)


def test_record_info_create_with_urn():
    record_info = record_info_create(
        validation_type_id="someValidationType",
        old_id="12345",
        permission_unit_id="somePermissionUnit",
        urn="urn:nbn:se:nordiskamuseet:some-nbn",
    )

    expected_xml = """
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>someValidationType</linkedRecordId>
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
            <urn>urn:nbn:se:nordiskamuseet:some-nbn</urn>
        </recordInfo>
    """

    assert_equal_for_xml_and_xml_string(record_info, expected_xml)
