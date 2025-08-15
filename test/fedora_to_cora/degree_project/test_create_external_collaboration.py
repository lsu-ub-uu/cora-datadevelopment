import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.degree_project.create_external_collaboration import create_external_collaboration


def test_create_external_collaboration():
    source_record = ET.fromstring(
        """
        <publication>
            <externalCooperation>
                <external>true</external>
                <partners>
                    <partner>
                        <name>En extern partner</name>
                    </partner>
                    <partner>
                        <name>Ytterligare extern partner</name>
                    </partner>
                </partners>
            </externalCooperation>
        </publication>
        """
    )

    external_collaboration = create_external_collaboration(source_record)

    assert_equal_for_xml_and_xml_string(
        external_collaboration,
        """
        <externalCollaboration>
            <namePart repeatId="0">
                En extern partner
            </namePart>
            <namePart repeatId="1">
                Ytterligare extern partner
            </namePart>
        </externalCollaboration>
        """,
    )
