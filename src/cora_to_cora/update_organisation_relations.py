from cora.cora_json_utils import (
    find_child_with_name_in_data,
    find_all_children_with_name_in_data,
    get_first_atomic_value_with_name_in_data,
)
from typing import Optional, Tuple, Any
import xml.etree.ElementTree as ET
from cora.update import update_record
from common.common_data import create_record_link_using_name_type_id
from cora.context import Context


def update_organisation_relations(
    old_and_new_org_pairs: list[Tuple[dict[str, Any], ET.Element]],
    context: Context,
):
    old_id_to_new_id_map = _create_old_id_to_new_id_map(old_and_new_org_pairs)

    for old_org, new_org in old_and_new_org_pairs:
        _update_organisation_relations_for_single_organisation(
            old_org, new_org, old_id_to_new_id_map, context
        )


def _create_old_id_to_new_id_map(
    old_and_new_org_pairs: list[Tuple[dict[str, Any], ET.Element]],
) -> dict[str, str]:
    old_id_to_new_id_map: dict[str, str] = {}
    for old_org, new_org in old_and_new_org_pairs:
        id = new_org.findtext("./recordInfo/id")
        old_id = new_org.findtext("./recordInfo/oldId")
        if id is not None and old_id is not None:
            old_id_to_new_id_map[old_id] = id
    return old_id_to_new_id_map


def _update_organisation_relations_for_single_organisation(
    old_org: dict,
    new_org: ET.Element,
    old_id_to_new_id_map: dict[str, str],
    context: Context,
):
    old_org_data = old_org["record"]["data"]
    old_org_organisation = find_child_with_name_in_data(
        old_org_data["children"], "organisation"
    )
    assert old_org_organisation is not None

    appended_earlier = _append_earlier_organisation_links(
        old_org_organisation, new_org, old_id_to_new_id_map
    )

    appended_parent = _append_parent_organisation_link(
        old_org_organisation, new_org, old_id_to_new_id_map
    )

    if appended_earlier or appended_parent:
        update_record(
            new_org,
            context,
        )


def _append_earlier_organisation_links(
    old_org_organisation: dict,
    new_org: ET.Element,
    old_id_to_new_id_map: dict[str, str],
) -> bool:
    old_org_earlier_organisations = find_all_children_with_name_in_data(
        old_org_organisation["children"], "earlierOrganisation"
    )
    if len(old_org_earlier_organisations) > 0:
        for index, old_org_earlier_organisation in enumerate(
            old_org_earlier_organisations
        ):
            new_org.append(
                _create_organisation_link(
                    old_org_earlier_organisation,
                    old_id_to_new_id_map,
                    "earlier",
                    str(index),
                )
            )
        return True
    return False


def _append_parent_organisation_link(
    old_org_organisation: dict,
    new_org: ET.Element,
    old_id_to_new_id_map: dict[str, str],
):
    old_org_parent_organisations = find_all_children_with_name_in_data(
        old_org_organisation["children"], "parentOrganisation"
    )
    if len(old_org_parent_organisations) > 1:
        raise AssertionError("Multiple parent organisations found")
    if len(old_org_parent_organisations) == 1:
        new_org.append(
            _create_organisation_link(
                old_org_parent_organisations[0], old_id_to_new_id_map, "parent"
            )
        )
        return True
    return False


def _create_organisation_link(
    old_org_parent_organisation: dict,
    old_id_to_new_id_map: dict[str, str],
    type: str,
    repeat_id: Optional[str] = None,
) -> ET.Element:
    if repeat_id is not None:
        related = ET.Element("related", type=type, repeatId=repeat_id)
    else:
        related = ET.Element("related", type=type)

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
