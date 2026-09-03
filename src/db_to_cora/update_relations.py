import xml.etree.ElementTree as ET
import logging
from common.threads import run_with_threads
from cora.context import Context
from cora.update import update_record
from common.common_data import create_record_link
from common.xml_utils import create_group

logger = logging.getLogger(__name__)


class RelationMapping:
    def __init__(
        self, old_relation_tag: str, new_relation_link: str, new_relation_type: str
    ):
        self.old_relation_tag = old_relation_tag
        self.new_relation_link = new_relation_link
        self.new_relation_type = new_relation_type


def update_relations(
    record_mapping: list[tuple[ET.Element, ET.Element | None]],
    relation_mappings: list[RelationMapping],
    record_type: str,
    context: Context,
):
    old_id_to_new_id_map = _create_old_id_to_new_id_map(record_mapping)
    run_with_threads(
        record_mapping,
        lambda org_pair: _update_relations_for_single_record(
            org_pair,
            old_id_to_new_id_map,
            relation_mappings,
            record_type,
            context,
        ),
        workers=context.get_workers(),
        desc=f"Updating {record_type} records with relations",
    )


def _update_relations_for_single_record(
    record_pair: tuple[ET.Element, ET.Element | None],
    old_id_to_new_id_map: dict[str, str],
    relation_mappings: list[RelationMapping],
    record_type: str,
    context: Context,
):
    modified = False
    old_record, new_record = record_pair
    if new_record is None:
        return
    new_record_data = new_record.find(f"./data/*")
    old_id = new_record.findtext("./oldId")
    assert new_record_data is not None

    for relation_mapping in relation_mappings:
        old_relation_tag = relation_mapping.old_relation_tag
        new_relation_type = relation_mapping.new_relation_type
        new_relation_link = relation_mapping.new_relation_link

        old_relation_ids = _get_old_relation_ids(old_record, old_relation_tag)
        for index, related_old_id in enumerate(old_relation_ids):
            if related_old_id in old_id_to_new_id_map:
                related_new_id = old_id_to_new_id_map[related_old_id]
                logger.info(
                    f"Adding relation with type {new_relation_type} from {old_id} to {related_old_id}"
                )
                new_record_data.append(
                    _create_related_item(
                        type=new_relation_type,
                        repeat_id=str(index),
                        link_name=new_relation_link,
                        record_type=record_type,
                        new_relation_id=related_new_id,
                    )
                )

                modified = True

    if modified:
        logger.info(
            f"Updating relations for {record_type} record with oldId {new_record.findtext('./oldId')}"
        )
        update_result = update_record(
            new_record_data,
            context,
        )
        if not update_result.success:
            raise Exception(
                f"Failed to update record with oldId {new_record.findtext('.//oldId')}: {update_result.error}"
            )


def _get_old_relation_ids(old_record: ET.Element, old_relation_tag: str) -> list[str]:
    old_relation_id_text = old_record.findtext(f"./{old_relation_tag}")
    return old_relation_id_text.split(",") if old_relation_id_text else []


def _create_related_item(
    type: str, repeat_id: str, link_name: str, record_type: str, new_relation_id: str
) -> ET.Element:
    related_item_element = create_group(
        "related",
        type=type,
        repeatId=repeat_id,
        children=[create_record_link(link_name, record_type, new_relation_id)],
    )
    assert related_item_element is not None
    return related_item_element


def _create_old_id_to_new_id_map(
    old_and_new_org_pairs: list[tuple[ET.Element, ET.Element | None]],
) -> dict[str, str]:
    old_id_to_new_id_map: dict[str, str] = {}
    for _, new_org in old_and_new_org_pairs:
        if new_org is None:
            continue
        id = new_org.findtext(".//recordInfo/id")
        old_id = new_org.findtext(".//recordInfo/oldId")
        if id is not None and old_id is not None:
            old_id_to_new_id_map[old_id] = id
    return old_id_to_new_id_map
