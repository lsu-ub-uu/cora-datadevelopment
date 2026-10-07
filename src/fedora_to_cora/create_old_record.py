import xml.etree.ElementTree as ET
import logging
from common.xml_utils import pretty_print_xml
from common.xml_utils import create_group, create_text
from cora.create import create_record
from cora.context import Context

logger = logging.getLogger(__name__)


def old_record_migrate(
    source_record: ET.Element,
    context: Context,
) -> ET.Element:
    old_record = transform_old_record(source_record)
    try:
        create_old_record_result = create_record(
            old_record, record_type="diva-oldRecord", context=context
        )
    except Exception as e:
        logger.error(f"Error transforming old record: {e}")
        raise
    return old_record


def transform_old_record(source_record: ET.Element) -> ET.Element:
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
