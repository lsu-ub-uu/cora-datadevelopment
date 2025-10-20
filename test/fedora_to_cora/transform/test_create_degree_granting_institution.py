from unittest.mock import patch
import xml.etree.ElementTree as ET

from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_degree_granting_institution import (
    create_degree_granting_institution,
)
from cora.context import MockContext

mock_context = MockContext("https://example.org/rest/record/", "test-token")


@patch(
    "fedora_to_cora.transform.create_degree_granting_institution.get_cora_id_by_old_id"
)
def test_create_degree_granting_institution_controlled(mock_get_cora_id_by_old_id):

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, *, record_type, context: (
        "cora-id-for-1956"
        if record_type == "diva-organisation" and old_id == "1956"
        else None
    )

    source_record = ET.fromstring(
        """
        <publication>
            <defence>
                <date>2022-07-31T16:19:00.000+02:00</date>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <room>
                    <name>Balsalen</name>
                    <street>Slottet</street>
                    <city>Uppsala</city>
                </room>
                <grantingInstitution>
                    <organisationId>1956</organisationId>
                    <organisationName>
                        <name>Uppsala universitet</name> 
                    </organisationName>
                    <organisationAddress>
                        <addressId>1956</addressId>
                        <postnumber>75105</postnumber>
                        <city>Uppsala</city>
                        <country>
                            <countryCode>se</countryCode>
                        </country>
                    </organisationAddress>
                </grantingInstitution>
            </defence>
        </publication>
        """
    )

    degree_granting_institutions = create_degree_granting_institution(
        source_record, mock_context
    )

    assert len(degree_granting_institutions) == 1

    assert_equal_for_xml_and_xml_string(
        degree_granting_institutions[0],
        """
           <degreeGrantingInstitution type="corporate" otherType="link">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-id-for-1956</linkedRecordId>
                </organisation>
                <role>
                    <roleTerm>dgg</roleTerm>
                </role>
           </degreeGrantingInstitution>
        """,
    )


def test_create_degree_granting_institution_uncontrolled():
    source_record = ET.fromstring(
        """
        <publication>
            <defence>
                <date>2022-07-31T16:19:00.000+02:00</date>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <room>
                    <name>Balsalen</name>
                    <street>Slottet</street>
                    <city>Uppsala</city>
                </room>
                <externalGrantingInstitution>
                    Lunds universitet
                </externalGrantingInstitution>
            </defence>
        </publication>
        """
    )

    degree_granting_institutions = create_degree_granting_institution(
        source_record, mock_context
    )
    assert len(degree_granting_institutions) == 1

    assert_equal_for_xml_and_xml_string(
        degree_granting_institutions[0],
        """
           <degreeGrantingInstitution type="corporate" otherType="text">
                <namePart>Lunds universitet</namePart>
                <role>
                    <roleTerm>dgg</roleTerm>
                </role>
           </degreeGrantingInstitution>
        """,
    )


@patch(
    "fedora_to_cora.transform.create_degree_granting_institution.get_cora_id_by_old_id"
)
def test_create_controlled_and_uncontrolled_institution(mock_get_cora_id_by_old_id):
    mock_get_cora_id_by_old_id.side_effect = lambda old_id, *, record_type, context: (
        "cora-id-for-1956"
        if record_type == "diva-organisation" and old_id == "1956"
        else None
    )

    source_record = ET.fromstring(
        """
        <publication>
            <defence>
                <date>2022-07-31T16:19:00.000+02:00</date>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <room>
                    <name>Balsalen</name>
                    <street>Slottet</street>
                    <city>Uppsala</city>
                </room>
                <grantingInstitution>
                    <organisationId>1956</organisationId>
                </grantingInstitution>
                <externalGrantingInstitution>
                    Lunds universitet
                </externalGrantingInstitution>
            </defence>
        </publication>
        """
    )

    degree_granting_institutions = create_degree_granting_institution(
        source_record, mock_context
    )
    assert len(degree_granting_institutions) == 2

    assert_equal_for_xml_and_xml_string(
        degree_granting_institutions[0],
        """
            <degreeGrantingInstitution type="corporate" otherType="link">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-id-for-1956</linkedRecordId>
                </organisation>
                <role>
                    <roleTerm>dgg</roleTerm>
                </role>
           </degreeGrantingInstitution>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        degree_granting_institutions[1],
        """
           <degreeGrantingInstitution type="corporate" otherType="text">
                <namePart>Lunds universitet</namePart>
                <role>
                    <roleTerm>dgg</roleTerm>
                </role>
           </degreeGrantingInstitution>
        """,
    )
