from fedora_to_cora import create_admin_info
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
