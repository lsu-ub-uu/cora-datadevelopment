from cora.cora_json_utils import (
    find_child_with_name_in_data,
    find_all_children_with_name_in_data,
    get_first_atomic_value_with_name_in_data,
)
from cora.create import (
    CreateRecordSuccessResult,
)
from typing import Literal, Tuple, Any
import xml.etree.ElementTree as ET
from cora.update import update_record
from common.common_data import create_record_link_using_name_type_id
from cora.context import Context


def update_organisation_relations(
    old_and_created_record_pairs: list[Tuple[dict[str, Any], ET.Element]],
    context: Context,
):
    old_id_to_new_id_map = _create_old_id_to_new_id_map(old_and_created_record_pairs)

    for old_org, created_org in old_and_created_record_pairs:
        _update_organisation_relations_for_single_organisation(
            old_org, created_org, old_id_to_new_id_map, context
        )


def _create_old_id_to_new_id_map(
    old_and_created_record_pairs: list[Tuple[dict[str, Any], ET.Element]],
) -> dict[str, str]:
    old_id_to_new_id_map: dict[str, str] = {}
    for old_org, created_org in old_and_created_record_pairs:
        id = created_org.findtext("./recordInfo/id")
        old_id = created_org.findtext("./recordInfo/oldId")
        if id is not None and old_id is not None:
            old_id_to_new_id_map[old_id] = id
    return old_id_to_new_id_map


def _update_organisation_relations_for_single_organisation(
    old_org: dict,
    created_org: ET.Element,
    old_id_to_new_id_map: dict[str, str],
    context: Context,
):
    old_org_data = old_org["record"]["data"]
    old_org_organisation = find_child_with_name_in_data(
        old_org_data["children"], "organisation"
    )
    assert old_org_organisation is not None

    old_org_parent_organisations = find_all_children_with_name_in_data(
        old_org_organisation["children"], "parentOrganisation"
    )
    if len(old_org_parent_organisations) > 1:
        raise AssertionError("Multiple parent organisations found")
    if len(old_org_parent_organisations) == 1:
        created_org.append(
            _create_parent_organisation_link(
                old_org_parent_organisations[0], old_id_to_new_id_map
            )
        )
        update_record(created_org, context)


def _create_parent_organisation_link(
    old_org_parent_organisation: dict, old_id_to_new_id_map: dict[str, str]
) -> ET.Element:
    related = ET.Element("related", type="parent")
    old_parent_link = find_child_with_name_in_data(
        old_org_parent_organisation["children"],
        "organisationLink",
    )
    assert old_parent_link is not None
    old_parent_id = get_first_atomic_value_with_name_in_data(
        old_parent_link["children"], "linkedRecordId"
    )
    assert old_parent_id is not None
    parent_new_id = old_id_to_new_id_map.get(old_parent_id)
    assert parent_new_id is not None
    related.append(
        create_record_link_using_name_type_id(
            "organisation", "diva-organisation", parent_new_id
        )
    )
    return related


""" {
    "new:1234": {
        old_id: "old:5678",
        parent_old_id: "old:91011",
        earlier_old_ids: ["old:1213", "old:1415"],
    },
    "new:2345": {old_id: "old:6789", parent_old_id: None, earlier_old_ids: []},
}
 """
