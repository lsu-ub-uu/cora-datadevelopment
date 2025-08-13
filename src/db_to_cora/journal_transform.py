import xml.etree.ElementTree as ET
#from common.xml_utils import append_if_value
from common.record_info_create import record_info_create
from common.common_data import create_title_info

nameInData = "journal"


def transform_journal(source_record: ET.Element) -> ET.Element:
    """
    Create a Cora journal element from a DB export journal.
    """

    journal = ET.Element(nameInData)
    
    journal.append(_create_record_info(source_record))
    journal.append(_create_title_info(source_record))
        
    return journal


def _create_record_info(source_record: ET.Element) -> ET.Element:
    source_old_id = source_record.find(".//old_id")
    assert (
        source_old_id is not None and source_old_id.text is not None
    ), "old_id is missing in source record"

    return record_info_create(
        validation_type_id="diva-journal",
        old_id=source_old_id.text,
        permission_unit_id=None,
    )
    
def _create_title_info(source_record: ET.Element) -> ET.Element:
    title = source_record.find(f".//title")
    if title is not None and title.text:
        return create_title_info(
            title.text)
    
    
