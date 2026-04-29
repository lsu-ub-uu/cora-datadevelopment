import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.degree_project.create_external_collaboration import (
    create_external_collaborations,
)


def test_create_external_collaboration():
    source_record = ET.fromstring("""
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
        """)

    external_collaborations = create_external_collaborations(source_record)

    assert len(external_collaborations) == 2

    assert_equal_for_xml_and_xml_string(
        external_collaborations[0],
        """
        <name type="corporate" otherType="externalCollaboration" repeatId="0">
            <role>
                <roleTerm>ctb</roleTerm>
            </role>
            <namePart>
                En extern partner
            </namePart>
        </name>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        external_collaborations[1],
        """
        <name type="corporate" otherType="externalCollaboration" repeatId="1">
            <role>
                <roleTerm>ctb</roleTerm>
            </role>
            <namePart>
                Ytterligare extern partner
            </namePart>
        </name>
        """,
    )


def test_create_externnal_true_without_name():
    source_record = ET.fromstring("""
        <publication>
            <externalCooperation>
                <external>true</external>
                <partners>
                    <partner>
                    </partner>
                </partners>
            </externalCooperation>
        </publication>
        """)

    external_collaborations = create_external_collaborations(source_record)

    assert len(external_collaborations) == 1

    assert_equal_for_xml_and_xml_string(
        external_collaborations[0],
        """
        <name type="corporate" otherType="externalCollaboration" repeatId="0">
            <role>
                <roleTerm>ctb</roleTerm>
            </role>
            <namePart>
                Externt samarbete
            </namePart>
        </name>
        """,
    )


def test_create_external_false_without_name():
    source_record = ET.fromstring("""
        <publication>
            <externalCooperation>
                <external>false</external>
                <partners>
                </partners>
            </externalCooperation>
        </publication>
        """)

    external_collaborations = create_external_collaborations(source_record)

    assert len(external_collaborations) == 0


def test_no_external_cooperation():
    source_record = ET.fromstring("""
        <publication>
        </publication>
        """)

    external_collaborations = create_external_collaborations(source_record)

    assert len(external_collaborations) == 0
