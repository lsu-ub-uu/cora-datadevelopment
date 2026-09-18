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

    single_role = _is_single_role_type(source_record)

    return [
        _create_name_type_corporate_from_organisation_id(
            org_id.text, context, single_role, index
        )
        for index, org_id in enumerate(responsible_organisation_ids)
        if org_id.text is not None and org_id.text.strip() != ""
    ]


def _is_single_role_type(source_record: ET.Element) -> bool:
    author_only_validation_types = {
        "conference_other",
    }
    return (
        get_validation_type_from_fedora_record(source_record)
        in author_only_validation_types
    )


def _create_name_type_corporate_from_organisation_id(
    old_id: str, context: Context, single_role: bool, repeat_id: int = 0
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
                    create_text(
                        "roleTerm",
                        repeatId=None if single_role else "0",
                        value="aut",
                    )
                ],
            ),
        ],
    )


def _get_role(source_record: ET.Element) -> str:
    validation_type = get_validation_type_from_fedora_record(source_record)
    if validation_type in ["publication_edited-book", "conference_proceeding"]:
        return "edt"
    return "aut"
