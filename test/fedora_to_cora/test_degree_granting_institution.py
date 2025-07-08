import xml.etree.ElementTree as ET
from fedora_to_cora.create_degree_granting_institution import create_degree_granting_institution
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext

def test_degree_granting_institution():
    mock_context = MockContext()

    source_record = ET.fromstring(
        """
        <publication>
            <defence>
                <grantingInstitution>
                    <organisationName>
                        <name>Uppsala universitet</name>
                    </organisationName>
                </grantingInstitution>
            </defence>
        </publication>
        """
    )
    institution = create_degree_granting_institution(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        institution,
        """
        <degreeGrantingInstitution type="corporate">
            <namePart>Uppsala universitet</namePart>
            <role>
                <roleTerm>
                    dgg
                </roleTerm>
            </role>
        </degreeGrantingInstitution>    
        """,
    )

def test_degree_granting_institution_with_linked_organisation(monkeypatch):
    organisation_old_id = "985"
    organisation_cora_id = "diva-organisation:21861441014837120"

    mock_context = MockContext()

    def mock_get_id(old_id, *args, **kwargs):
        if old_id == organisation_old_id:
            return organisation_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.create_degree_granting_institution.get_cora_id_by_old_id",
        mock_get_id,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <defence>
                <grantingInstitution>
                    <organisationId>{organisation_old_id}</organisationId>
                </grantingInstitution>
            </defence>
        </publication>
        """
    )

    institution = create_degree_granting_institution(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        institution,
        """
        <degreeGrantingInstitution type="corporate">
            <organisation>
                <linkedRecordType>diva-organisation</linkedRecordType>
                <linkedRecordId>diva-organisation:21861441014837120</linkedRecordId>
            </organisation>
            <role>
                <roleTerm>
                    dgg
                </roleTerm>
            </role>
        </degreeGrantingInstitution>    
        """,
    )