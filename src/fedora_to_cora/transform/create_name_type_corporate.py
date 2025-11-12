import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from cora.context import Context


def create_name_type_corporate(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    responsible_organisation_ids = source_record.findall(
        "./responsibleOrganisations/organisation/organisationId"
    )

    return [
        _create_name_type_corporate_from_organisation_id(org_id.text, context, index)
        for index, org_id in enumerate(responsible_organisation_ids)
        if org_id.text is not None and org_id.text.strip() != ""
    ]


def _create_name_type_corporate_from_organisation_id(
    old_id: str, context: Context, repeat_id: int = 0
) -> ET.Element:
    name = ET.Element("name", type="corporate", repeatId=str(repeat_id))

    old_id = get_cora_id_by_old_id(
        old_id, record_type="diva-organisation", context=context
    )

    organisation_link = create_record_link_using_name_type_id(
        name_in_data="organisation", record_type="diva-organisation", record_id=old_id
    )

    name.append(organisation_link)

    role = ET.SubElement(name, "role")
    ET.SubElement(role, "roleTerm").text = "cre"

    return name
