import xml.etree.ElementTree as ET
from common.record_info_create import record_info_create
from common.common_data import name_type_corporate_create

nameInData = "publisher"


def transform_publisher(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora publisher element from a DB export publisher.
    """

    publisher = ET.Element(nameInData)

    publisher.append(_create_record_info(source_record))
    publisher.append(_create_name(source_record))

    return publisher


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-publisher",
        old_id=source_old_id.text,
        permission_unit_id=None,
    )


def _create_name(source_record: ET.Element) -> ET.Element:
    name = source_record.find(".//name")
    assert (
        name is not None and name.text is not None
    ), "name is missing in source record"

    return name_type_corporate_create(name.text)
