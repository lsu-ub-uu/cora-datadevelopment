import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from common.xml_utils import append_if_value, create_group, create_text

DIVA_ORGANISATION_RECORD_TYPE = "diva-organisation"


def create_degree_granting_institution(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    degree_granting_institutions = []

    organisation_old_id = source_record.findtext(
        "./defence/grantingInstitution/organisationId"
    )
    if organisation_old_id is not None:
        degree_granting_institutions.append(
            _create_controlled_degree_granting_institution(organisation_old_id, context)
        )

    external_granting_institution = source_record.findtext(
        "./defence/externalGrantingInstitution"
    )

    if external_granting_institution is not None:
        degree_granting_institutions.append(
            _create_uncontrolled_degree_granting_institution(
                external_granting_institution
            )
        )

    return degree_granting_institutions


def _create_controlled_degree_granting_institution(
    organisation_old_id: str, context: Context
):
    return create_group(
        "name",
        type="corporate",
        otherType="degreeGrantingInstitution",
        children=[
            create_record_link(
                name_in_data="organisation",
                record_type=DIVA_ORGANISATION_RECORD_TYPE,
                record_id=get_cora_id_by_old_id(
                    organisation_old_id,
                    record_type=DIVA_ORGANISATION_RECORD_TYPE,
                    context=context,
                ),
            ),
            _create_role(),
        ],
    )


def _create_uncontrolled_degree_granting_institution(
    external_granting_institution: str,
):
    return create_group(
        "name",
        type="corporate",
        otherType="degreeGrantingInstitution",
        children=[
            create_text("namePart", external_granting_institution),
            _create_role(),
        ],
    )


def _create_role():
    role = ET.Element("role")
    role_term_element = ET.SubElement(role, "roleTerm")
    role_term_element.text = "dgg"
    return role
