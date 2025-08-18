import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_extent import create_extent


def test_create_extent():
    source_record = ET.fromstring(
        """
        <publication>
            <pages>208</pages>
        </publication>
        """
    )

    origin_info = create_extent(source_record)

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
            <extent>208</extent>
        """,
    )


def test_create_extent_missing():
    source_record = ET.fromstring(
        """
        <publication>
            <pages>208</pages>
        </publication>
        """
    )

    origin_info = create_extent(source_record)

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
            <extent>208</extent>
        """,
    )
