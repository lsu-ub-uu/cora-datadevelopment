import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value

DIVA_ORGANISATION_RECORD_TYPE = "diva-organisation"


def create_degree_granting_institution(
    source_record: ET.Element, context: Context
) -> ET.Element:
    degree_granting_institution = ET.Element(
        "degreeGrantingInstitution", type="corporate"
    )
    organisation_name = source_record.findtext(
        "./defence/grantingInstitution/organisationName/name"
    )
    organisation_old_id = source_record.findtext(
        "./defence/grantingInstitution/organisationId"
    )

    if organisation_old_id is not None:
        cora_id = get_cora_id_by_old_id(
            organisation_old_id,
            record_type=DIVA_ORGANISATION_RECORD_TYPE,
            context=context,
        )
        organisation = create_record_link_using_name_type_id(
            name_in_data="organisation",
            record_type=DIVA_ORGANISATION_RECORD_TYPE,
            record_id=cora_id,
        )
        append_if_value(degree_granting_institution, organisation)

    if organisation_name is not None:
        name_part = ET.SubElement(degree_granting_institution, "namePart")
        name_part.text = organisation_name

    role = ET.SubElement(degree_granting_institution, "role")
    role_term_element = ET.SubElement(role, "roleTerm")
    role_term_element.text = "dgg"

    return degree_granting_institution
