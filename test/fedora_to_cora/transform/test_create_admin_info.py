from fedora_to_cora.transform.create_admin_info import create_admin_info
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_admin_info():
    source_record = ET.fromstring(
        """
        <publication>
            <reviewed>true</reviewed>
            <internalNote>Intern anmärkning</internalNote>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <adminInfo>
                <note type="internal">Intern anmärkning</note>
                <reviewed>true</reviewed>
            </adminInfo>
        """,
    )


def test_create_admin_info_when_no_note():
    source_record = ET.fromstring(
        """
        <publication>
            <reviewed>true</reviewed>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <adminInfo>
                <reviewed>true</reviewed>
            </adminInfo>
        """,
    )


def test_create_admin_info_when_no_reviewed():
    source_record = ET.fromstring(
        """
        <publication>
            <internalNote>Intern anmärkning</internalNote>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <adminInfo>
                <note type="internal">Intern anmärkning</note>
            </adminInfo>
        """,
    )


def test_create_admin_info_failed_true():
    source_record = ET.fromstring(
        """
        <publication>
            <failed>true</failed>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <adminInfo>
                <failed>true</failed>
            </adminInfo>
        """,
    )


def test_create_admin_info_failed_false():
    source_record = ET.fromstring(
        """
        <publication>
            <failed>false</failed>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert admin is None


def test_create_admin_info_when_no_note_and_no_reviewed():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    admin = create_admin_info(source_record)

    assert admin is None
