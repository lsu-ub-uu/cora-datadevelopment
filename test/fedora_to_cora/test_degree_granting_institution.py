import xml.etree.ElementTree as ET
from fedora_to_cora.create_degree_granting_institution import create_degree_granting_institution
from common.test_helper import assert_equal_for_xml_and_xml_string

def test_degree_granting_institution():
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

    institution = create_degree_granting_institution(source_record)

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
    # assert_equal_for_xml_and_xml_string(
    #     classifications[0],
    #     """
    #     <degreeGrantingInstitution type="corporate">
    #         <organisation>
    #             <linkedRecordType>diva-organisation</linkedRecordType>
    #             <linkedRecordId>{id}</linkedRecordId>
    #         </organisation>
    #         <namePart>
    #             Uppsala universitet
    #         </namePart>
    #         <role>
    #             <roleTerm>
    #                 dgg
    #             </roleTerm>
    #         </role>
    #     </degreeGrantingInstitution>    
    #     """,
    # )