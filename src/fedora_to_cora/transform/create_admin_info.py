import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_note import create_note
from common.xml_utils import append_if_value, create_group, create_text


def create_admin_info(source_record: ET.Element) -> ET.Element | None:
    """
    Create an admin element with internal notes and reviewed status.
    """

    failed = source_record.findtext("./failed")

    return create_group(
        "adminInfo",
        children=[
            create_note(
                source_record,
                type="internal",
                source_selector="./internalNote",
            ),
            create_text("reviewed", source_record.findtext("./reviewed")),
            create_text("failed", failed if failed and failed == "true" else None),
        ],
    )
