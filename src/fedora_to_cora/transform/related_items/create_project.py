import xml.etree.ElementTree as ET
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from common.xml_utils import append_if_value, create_group


def create_related_item_type_project(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
    """
    Create relatedItem elements of type project from the source record.

    Creates links to project for projectRelations elements with pd and fills data from projects.
    """
    controlled_items = _create_related_items_from_controlled_projects(
        source_record, context
    )
    uncontrolled_items = _create_related_items_from_uncontrolled_projects(source_record)

    return controlled_items + uncontrolled_items


def _create_related_items_from_controlled_projects(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
    controlled_project_ids = source_record.findall(
        "./projectRelations/projectRelation/pid"
    )
    return [
        _create_controlled_project_link(pid.text, f"controlled{i}", context)
        for i, pid in enumerate(controlled_project_ids)
        if pid.text
    ]


def _create_controlled_project_link(
    pid: str, repeat_id: str, context: Context
) -> ET.Element | None:
    """
    Create a relatedItem element of type project with a controlled project link.
    """

    project_cora_id = get_cora_id_by_old_id(
        pid, record_type="diva-project", context=context
    )

    return create_group(
        "relatedItem",
        type="project",
        otherType="link",
        repeatId=repeat_id,
        children=[
            create_record_link_using_name_type_id(
                name_in_data="project",
                record_type="diva-project",
                record_id=project_cora_id,
            )
        ],
    )


def _create_related_items_from_uncontrolled_projects(
    source_record: ET.Element,
) -> list[ET.Element | None]:
    uncontrolled_project_ids = source_record.findall("./projects/project/projectName")

    return [
        _create_uncontrolled_project(project_xml, f"uncontrolled{i}")
        for i, project_xml in enumerate(uncontrolled_project_ids)
    ]


def _create_uncontrolled_project(
    source_project: ET.Element, repeat_id: str
) -> ET.Element | None:
    """
    Create a relatedItem element of type project with an uncontrolled project link.
    """
    return create_group(
        "relatedItem",
        type="project",
        otherType="text",
        repeatId=repeat_id,
        children=[_create_title_info(source_project.text)],
    )


def _create_title_info(title: str | None) -> ET.Element:
    """
    Create a titleInfo element with the given title.
    """

    title_info = ET.Element("titleInfo")
    title_element = ET.SubElement(title_info, "title")
    title_element.text = title

    return title_info
