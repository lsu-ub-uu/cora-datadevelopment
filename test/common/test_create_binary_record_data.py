import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from common.create_binary_record_data import create_binary_record_data


def test_create_binary_record_data_full():
    binary = create_binary_record_data(
        visibility="published",
        host_record_type="someType",
        host_record_id="someId",
        original_file_name="file.txt",
        expected_file_size="123",
        expected_checksum="abc",
    )

    assert_equal_for_xml_and_xml_string(
        binary,
        """
        <binary type="generic">
            <recordInfo>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>genericBinary</linkedRecordId>
                </validationType>
                <visibility>published</visibility>
                <hostRecord>
                    <linkedRecordType>someType</linkedRecordType>
                    <linkedRecordId>someId</linkedRecordId>  
                </hostRecord>
                <status>created</status>
            </recordInfo>
            <originalFileName>file.txt</originalFileName>
            <expectedFileSize>123</expectedFileSize>
            <expectedChecksum>abc</expectedChecksum>
        </binary>
        """,
    )


def test_create_binary_record_data_minimal():
    binary = create_binary_record_data(
        visibility="published",
        host_record_type="someType",
        host_record_id="someId",
        original_file_name="file.txt",
        expected_file_size=None,
        expected_checksum=None,
    )
    assert_equal_for_xml_and_xml_string(
        binary,
        """
        <binary type="generic">
            <recordInfo>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>genericBinary</linkedRecordId>
                </validationType>
                <visibility>published</visibility>
                <hostRecord>
                    <linkedRecordType>someType</linkedRecordType>
                    <linkedRecordId>someId</linkedRecordId>  
                </hostRecord>
                <status>created</status>
            </recordInfo>
            <originalFileName>file.txt</originalFileName>
        </binary>
        """,
    )
