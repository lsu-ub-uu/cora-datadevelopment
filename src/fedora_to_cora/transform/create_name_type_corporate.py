import xml.etree.ElementTree as ET
from common.common_data import create_record_link
from common.xml_utils import create_group, create_text
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from cora.context import Context
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


def create_name_type_corporate(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
    responsible_organisation_ids = source_record.findall(
        "./responsibleOrganisations/organisation/organisationId"
    )

    author_only = _is_author_only_type(source_record)

    return [
        _create_name_type_corporate_from_organisation_id(
            org_id.text, context, author_only, index
        )
        for index, org_id in enumerate(responsible_organisation_ids)
        if org_id.text is not None and org_id.text.strip() != ""
    ]


def _is_author_only_type(source_record: ET.Element) -> bool:
    author_only_validation_types = {
        "conference_paper",
        "conference_other",
        "publication_preprint",
    }
    return (
        get_validation_type_from_fedora_record(source_record)
        in author_only_validation_types
    )


def _create_name_type_corporate_from_organisation_id(
    old_id: str, context: Context, author_only: bool, repeat_id: int = 0
):
    return create_group(
        "name",
        type="corporate",
        repeatId=str(repeat_id),
        children=[
            create_record_link(
                name_in_data="organisation",
                record_type="diva-organisation",
                record_id=get_cora_id_by_old_id(
                    old_id, record_type="diva-organisation", context=context
                ),
            ),
            create_group(
                "role",
                [
                    (
                        create_text("roleTerm", "aut")
                        if author_only
                        else create_text(
                            "roleTerm",
                            "cre",
                            repeatId="0",
                        )
                    )
                ],
            ),
        ],
    )
    name = ET.Element("name", type="corporate", repeatId=str(repeat_id))

    old_id = get_cora_id_by_old_id(
        old_id, record_type="diva-organisation", context=context
    )

    organisation_link = create_record_link(
        name_in_data="organisation", record_type="diva-organisation", record_id=old_id
    )

    name.append(organisation_link)

    role = ET.SubElement(name, "role")
    if author_only:
        ET.SubElement(role, "roleTerm").text = "aut"
    else:
        ET.SubElement(role, "roleTerm", repeatId="0").text = "cre"

    return name
