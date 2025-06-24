import xml.etree.ElementTree as ET
from fedora_to_cora.create_identifier_type_isrn import create_identifier_type_isrn
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_identifier_type_isrn():
    source_record = ET.fromstring(
        """
        <publication>
            <isrn>ISRN-SE-1234-5678</isrn>
        </publication>
        """
    )

    identifiers = create_identifier_type_isrn(source_record)

    assert_equal_for_xml_and_xml_string(
        identifiers,
        """
        <identifier type="isrn">ISRN-SE-1234-5678</identifier>
        """,
    )
