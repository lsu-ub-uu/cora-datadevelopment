from common.xml_utils import append_if_value
from cora.cora_json_utils import (
    find_child_with_name_in_data,
    find_all_children_with_name_in_data,
    get_first_atomic_value_with_name_in_data,
)
from typing import Optional, Tuple, Any
import xml.etree.ElementTree as ET
from cora.update import update_record
from common.common_data import create_record_link
from cora.context import Context
from common.threads import run_with_threads


def update_organisation_relations(
    old_and_new_org_pairs: list[Tuple[dict[str, Any], ET.Element]],
    context: Context,
):
    old_id_to_new_id_map = _create_old_id_to_new_id_map(old_and_new_org_pairs)

    run_with_threads(
        old_and_new_org_pairs,
        lambda org_pair: _update_organisation_relations_for_single_organisation(
            org_pair, old_id_to_new_id_map, context
        ),
        workers=context.get_workers(),
        desc="Updating organisation relations",
    )


def _create_old_id_to_new_id_map(
    old_and_new_org_pairs: list[Tuple[dict[str, Any], ET.Element]],
) -> dict[str, str]:
    old_id_to_new_id_map: dict[str, str] = {}
    for _, new_org in old_and_new_org_pairs:
        id = new_org.findtext("./data/organisation/recordInfo/id")
        old_id = new_org.findtext("./data/organisation/recordInfo/oldId")
        if id is not None and old_id is not None:
            old_id_to_new_id_map[old_id] = id
    return old_id_to_new_id_map


def _update_organisation_relations_for_single_organisation(
    org_pair: Tuple[dict[str, Any], ET.Element],
    old_id_to_new_id_map: dict[str, str],
    context: Context,
):
    old_org, new_org = org_pair
    old_org_data = old_org["record"]["data"]
    new_org_data = new_org.find("./data/organisation")
    assert new_org_data is not None

    appended_earlier = _append_earlier_organisation_links(
        old_org_data, new_org_data, old_id_to_new_id_map
    )

    appended_parent = _append_parent_organisation_link(
        old_org_data, new_org_data, old_id_to_new_id_map
    )

    if appended_earlier or appended_parent:
        update_record(
            new_org,
            context,
        )


def _append_earlier_organisation_links(
    old_org_organisation: dict,
    new_org_data: ET.Element,
    old_id_to_new_id_map: dict[str, str],
) -> bool:
    old_org_earlier_organisations = find_all_children_with_name_in_data(
        old_org_organisation["children"], "earlierOrganisation"
    )
    if len(old_org_earlier_organisations) > 0:
        for index, old_org_earlier_organisation in enumerate(
            old_org_earlier_organisations
        ):
            append_if_value(
                new_org_data,
                _create_organisation_link(
                    old_org_earlier_organisation,
                    old_id_to_new_id_map,
                    "earlier",
                    str(index),
                ),
            )
        return True
    return False


def _append_parent_organisation_link(
    old_org_organisation: dict,
    new_org_data: ET.Element,
    old_id_to_new_id_map: dict[str, str],
):
    old_org_parent_organisations = find_all_children_with_name_in_data(
        old_org_organisation["children"], "parentOrganisation"
    )
    if len(old_org_parent_organisations) > 1:
        raise AssertionError("Multiple parent organisations found")
    if len(old_org_parent_organisations) == 1:
        append_if_value(
            new_org_data,
            _create_organisation_link(
                old_org_parent_organisations[0], old_id_to_new_id_map, "parent"
            ),
        )
        return True
    return False


def _create_organisation_link(
    old_org_parent_organisation: dict,
    old_id_to_new_id_map: dict[str, str],
    type: str,
    repeat_id: Optional[str] = None,
) -> ET.Element | None:
    if repeat_id is not None:
        related = ET.Element("related", type=type, repeatId=repeat_id)
    else:
        related = ET.Element("related", type=type)

    old_parent_link = find_child_with_name_in_data(
        old_org_parent_organisation["children"],
        "organisationLink",
    )
    assert old_parent_link is not None
    old_parent_type = get_first_atomic_value_with_name_in_data(
        old_parent_link["children"], "linkedRecordType"
    )
    if old_parent_type == "rootOrganisation":
        return None

    old_parent_id = get_first_atomic_value_with_name_in_data(
        old_parent_link["children"], "linkedRecordId"
    )
    assert old_parent_id is not None
    parent_new_id = old_id_to_new_id_map.get(old_parent_id)
    if parent_new_id is None:
        print(
            f"Warning: No new ID found for old organisation ID {old_parent_id}. Skipping link creation."
        )
        return None
    related.append(
        create_record_link("organisation", "diva-organisation", parent_new_id)
    )
    return related
