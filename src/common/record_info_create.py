import xml.etree.ElementTree as ET
from common.common_data import create_record_link
from common.xml_utils import create_group, create_text


def record_info_create(
    validation_type_id: str,
    old_id: str | None = None,
    permission_unit_id: str | None = None,
    visibility: str | None = None,
    host_record_link: ET.Element | None = None,
    urn: str | None = None,
) -> ET.Element:
    record_info = create_group(
        "recordInfo",
        children=[
            create_record_link(
                name_in_data="validationType",
                record_type="validationType",
                record_id=validation_type_id,
            ),
            create_record_link(
                name_in_data="dataDivider", record_type="system", record_id="divaData"
            ),
            (
                create_record_link(
                    name_in_data="permissionUnit",
                    record_type="permissionUnit",
                    record_id=permission_unit_id,
                )
                if permission_unit_id is not None
                else None
            ),
            create_text("visibility", visibility) if visibility is not None else None,
            create_text("oldId", old_id) if old_id is not None else None,
            create_text("urn", urn) if urn is not None else None,
            host_record_link,
        ],
    )
    assert record_info is not None
    return record_info
