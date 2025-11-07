import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id


def create_related_item_type_funder(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    funder_infos = source_record.findall("./funderInfos/funderInfo")
    if funder_infos is None:
        return []

    return [
        _create_funder_related_item(funder_info, context, index)
        for index, funder_info in enumerate(funder_infos)
        if funder_info is not None and len(funder_info) > 0
    ]


def _create_funder_related_item(funder_info: ET.Element, context: Context, index: int):
    related_item = ET.Element("relatedItem", type="funder", repeatId=str(index))

    append_if_value(
        related_item,
        _create_funder_link(funder_info, context),
    )

    append_if_value(
        related_item,
        _create_project_identifier(funder_info),
    )

    return related_item


def _create_funder_link(funder_info: ET.Element, context: Context) -> ET.Element | None:
    funder_old_id = funder_info.findtext("./funder/funderId")

    if funder_old_id is None:
        return None
    funder_cora_id = get_cora_id_by_old_id(
        old_id=funder_old_id,
        context=context,
        record_type="diva-funder",
    )
    return create_record_link_using_name_type_id(
        "funder",
        "diva-funder",
        funder_cora_id,
    )


def _create_project_identifier(funder_info: ET.Element) -> ET.Element | None:
    project_number = funder_info.findtext("./projectNumber")
    if project_number is None:
        return None

    identifier = ET.Element("identifier", type="project")
    identifier.text = project_number
    return identifier
