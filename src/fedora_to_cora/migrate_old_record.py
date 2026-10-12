import xml.etree.ElementTree as ET
import logging
from common.common_data import create_record_link
from common.xml_utils import pretty_print_xml
from common.xml_utils import create_group, create_text
from cora.create import create_record, is_success_result
from cora.context import Context

logger = logging.getLogger(__name__)


def old_record_migrate(
    source_record: ET.Element,
    context: Context,
) -> tuple[bool, list[str] | None, str | None]:
    old_record = transform_old_record(source_record)
    try:
        result = create_record(
            old_record, record_type="diva-oldRecord", context=context
        )
    except Exception as e:
        logger.error(f"Error transforming old record: {e}")
        return False, [str(e)], None

    if is_success_result(result):
        return True, None, result.record_id
    return False, [result.error], None


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


def update_record_info(cora_old_record_id: str, output: ET.Element) -> ET.Element:
    assert output is not None, "record should not be None"
    assert cora_old_record_id is not None, "pid should not be None"
    record_info = output.find("recordInfo")
    assert record_info is not None, "recordInfo should not be None"
    old_record_tag = create_record_link(
        "oldRecord", "diva-oldRecord", cora_old_record_id
    )
    assert old_record_tag is not None, "old_record_tag should not be None"
    record_info.append(old_record_tag)
    return output
