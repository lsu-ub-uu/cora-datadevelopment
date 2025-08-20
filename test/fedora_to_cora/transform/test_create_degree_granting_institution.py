import xml.etree.ElementTree as ET

from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_degree_granting_institution import (
    create_degree_granting_institution,
)
from cora.context import MockContext

mock_context = MockContext("https://example.org/rest/record/", "test-token")


# def test_create_degree_granting_institution():
#     source_record = ET.fromstring(
#         """
#         <publication>
#             <defence>
#                 <date>2022-07-31T16:19:00.000+02:00</date>
#                 <language>
#                     <languageCode3>swe</languageCode3>
#                 </language>
#                 <room>
#                     <name>Balsalen</name>
#                     <street>Slottet</street>
#                     <city>Uppsala</city>
#                 </room>
#                 <grantingInstitution>
#                     <organisationName>
#                         <name>Uppsala universitet</name>
#                     </organisationName>
#                     <organisationAddress>
#                         <addressId>1956</addressId>
#                         <postnumber>75105</postnumber>
#                         <city>Uppsala</city>
#                         <country>
#                             <countryCode>se</countryCode>
#                         </country>
#                     </organisationAddress>
#                 </grantingInstitution>
#             </defence>
#         </publication>
#         """
#     )

#     admin = create_degree_granting_institution(source_record, mock_context)

#     assert_equal_for_xml_and_xml_string(
#         admin,
#         """
#             <adminInfo>
#                 <note type="internal">Intern anmärkning</note>
#                 <reviewed>true</reviewed>
#             </adminInfo>
#         """,
#     )
