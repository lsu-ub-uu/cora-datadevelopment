from operator import index
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.context import Context
from cora.update import update_record
from common.common_data import create_record_link_using_name_type_id


def update_relations(
    record_mapping: list[tuple[ET.Element, ET.Element]],
    relations_mapping: list[tuple[str, str]],
    record_type: str,
    link_name: str,
    context: Context,
):
    old_id_to_new_id_map = _create_old_id_to_new_id_map(record_mapping)
    run_with_threads(
        record_mapping,
        lambda org_pair: _update_relations_for_single_record(
            org_pair,
            old_id_to_new_id_map,
            relations_mapping,
            record_type,
            link_name,
            context,
        ),
        workers=context.get_workers(),
        desc=f"Updating {record_type} records with relations",
    )


def _update_relations_for_single_record(
    record_pair: tuple[ET.Element, ET.Element],
    old_id_to_new_id_map: dict[str, str],
    relations_mapping: list[tuple[str, str]],
    record_type: str,
    link_name: str,
    context: Context,
):
    modified = False
    old_record, new_record = record_pair
    new_record_data = new_record.find(f"./data/{link_name}")
    assert new_record_data is not None

    for old_relation_tag, new_relation_type in relations_mapping:
        old_relation_ids = _get_old_relation_ids(old_record, old_relation_tag)
        for index, old_relation_id in enumerate(old_relation_ids):
            if old_relation_id in old_id_to_new_id_map:
                new_relation_id = old_id_to_new_id_map[old_relation_id]

                new_record_data.append(
                    _create_related_item(
                        type=new_relation_type,
                        repeat_id=str(index),
                        link_name=link_name,
                        record_type=record_type,
                        new_relation_id=new_relation_id,
                    )
                )

                modified = True

    if modified:
        update_record(
            new_record_data,
            context,
        )


def _get_old_relation_ids(old_record: ET.Element, old_relation_tag: str) -> list[str]:
    old_relation_id_text = old_record.findtext(f"./{old_relation_tag}")
    return old_relation_id_text.split(",") if old_relation_id_text else []


def _create_related_item(
    type: str, repeat_id: str, link_name: str, record_type: str, new_relation_id: str
) -> ET.Element:
    related_item_element = ET.Element(
        "relatedItem", {"type": type, "repeatId": repeat_id}
    )
    related_item_element.append(
        create_record_link_using_name_type_id(link_name, record_type, new_relation_id)
    )
    return related_item_element


def _create_old_id_to_new_id_map(
    old_and_new_org_pairs: list[tuple[ET.Element, ET.Element]],
) -> dict[str, str]:
    old_id_to_new_id_map: dict[str, str] = {}
    for _, new_org in old_and_new_org_pairs:
        id = new_org.findtext(".//recordInfo/id")
        old_id = new_org.findtext(".//recordInfo/oldId")
        if id is not None and old_id is not None:
            old_id_to_new_id_map[old_id] = id
    return old_id_to_new_id_map
