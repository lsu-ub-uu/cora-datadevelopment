import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id


def record_info_create(
    validation_type_id: str, old_id: str, permission_unit_id: str | None = None
) -> ET.Element:
    record_info = ET.Element("recordInfo")

    record_info.append(
        create_record_link_using_name_type_id(
            name_in_data="validationType",
            record_type="validationType",
            record_id=validation_type_id,
        )
    )

    record_info.append(
        create_record_link_using_name_type_id(
            name_in_data="dataDivider", 
            record_type="system", 
            record_id="divaData"
        )
    )

    if permission_unit_id is not None:
        record_info.append(
            create_record_link_using_name_type_id(
                name_in_data="permissionUnit",
                record_type="permissionUnit",
                record_id=permission_unit_id,
            )
        )

    ET.SubElement(record_info, "oldId").text = old_id

    return record_info
