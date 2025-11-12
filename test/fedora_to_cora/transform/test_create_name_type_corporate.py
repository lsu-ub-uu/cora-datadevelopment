import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_name_type_corporate import (
    create_name_type_corporate,
)
from unittest.mock import patch
from cora.context import MockContext


def test_no_responsible_organisation():
    source_record = ET.fromstring("<publication></publication>")

    names = create_name_type_corporate(source_record, MockContext())

    assert len(names) == 0


def test_empty_responsible_organisation():
    source_record = ET.fromstring(
        """
        <publication>
            <responsibleOrganisations>
                <organisation>
                </organisation>
            </responsibleOrganisations>
        </publication>             
    """
    )

    names = create_name_type_corporate(source_record, MockContext())

    assert len(names) == 0


@patch("fedora_to_cora.transform.create_name_type_corporate.get_cora_id_by_old_id")
def test_create_name_type_corporate_from_responsible_organisation(mock_get_cora_id):
    mock_get_cora_id.side_effect = lambda old_id, record_type, context: {
        "879600": "org-12345",
        "879601": "org-67890",
    }.get(old_id, "default-id")

    source_record = ET.fromstring(
        """
        <publication>
            <responsibleOrganisations>
                <organisation>
                    <organisationId>879600</organisationId>
                </organisation>
                <organisation>
                    <organisationId>879601</organisationId>
                </organisation>
            </responsibleOrganisations>
        </publication>
    """
    )

    names = create_name_type_corporate(source_record, MockContext())
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="corporate" repeatId="0">
            <organisation>
                <linkedRecordType>diva-organisation</linkedRecordType>
                <linkedRecordId>org-12345</linkedRecordId>
            </organisation>
            <role><roleTerm>cre</roleTerm></role>
        </name>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        names[1],
        """<name type="corporate" repeatId="1">
            <organisation>
                <linkedRecordType>diva-organisation</linkedRecordType>
                <linkedRecordId>org-67890</linkedRecordId>
            </organisation>
            <role><roleTerm>cre</roleTerm></role>
        </name>
        """,
    )
