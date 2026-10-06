import xml.etree.ElementTree as ET
from common.xml_utils import pretty_print_xml
from common.xml_utils import create_group, create_text


def create_old_record(source_record: ET.Element) -> ET.Element:
    old_record = create_group(
        "oldRecord",
        children=[
            create_group(
                "recordInfo",
                children=[
                    create_text("id", value=source_record.findtext("./pid")),
                    create_group(
                        "validationType",
                        children=[
                            create_text("linkedRecordType", value="validationType"),
                            create_text("linkedRecordId", value="diva-oldRecord"),
                        ],
                    ),
                    create_group(
                        "dataDivider",
                        children=[
                            create_text("linkedRecordType", value="system"),
                            create_text("linkedRecordId", value="divaData"),
                        ],
                    ),
                    create_text("oldId", value=source_record.findtext("./pid")),
                ],
            ),
            create_text(
                "recordXml", value=f"<![CDATA[{pretty_print_xml(source_record)}]]>"
            ),
        ],
    )
    assert old_record is not None
    return old_record
