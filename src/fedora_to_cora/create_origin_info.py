import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link_using_name_type_id
from cora.context import Context
from common.xml_utils import append_if_value


def create_origin_info(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    """
    Create an origin_info element
    """
    origin_info = ET.Element("originInfo")

    append_if_value(origin_info, _create_date_issued(source_record))
    append_if_value(origin_info, _create_agent(source_record, context))

    # TODO agent/publisher/publisher publication/publisher/publishingHouse/publishingHouseId
    # TODO agent/namePart publication/publisher/publisherName
    # TODO agent/role/roleTerm = "pbl"
    # TODO place publication/publisher/city
    # TODO edition publication/edition

    if len(origin_info) == 0:
        return None

    return origin_info


def _create_date_issued(source_record: ET.Element) -> ET.Element | None:
    """
    Create a date_issued element
    """
    source_date_issued = source_record.find("./dateIssued")
    if source_date_issued is None or source_date_issued.text is None:
        return None

    date_issued = ET.Element("dateIssued")
    ET.SubElement(date_issued, "year").text = source_date_issued.text

    return date_issued


def _create_agent(source_record: ET.Element, context: Context) -> ET.Element | None:
    """
    Create an agent element from publisher
    """
    publisher = source_record.find("./publisher")

    if publisher is None:
        return None

    agent = ET.Element("agent")

    publisher_name = publisher.find("./publisherName")
    if publisher_name is not None and publisher_name.text:
        ET.SubElement(agent, "namePart", repeatId="0").text = publisher_name.text

    append_if_value(agent, _create_publisher_link(publisher, context))

    if len(agent) > 0:
        role = ET.SubElement(agent, "role")
        ET.SubElement(role, "roleTerm").text = "pbl"

    return agent


def _create_publisher_link(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    publishing_house_id = source_record.find("./publishingHouse/publishingHouseId")

    if publishing_house_id is None or publishing_house_id.text is None:
        return None

    cora_publisher_id = get_cora_id_by_old_id(
        publishing_house_id.text, record_type="diva-publisher", context=context
    )
    return create_record_link_using_name_type_id(
        "publisher", "diva-publisher", cora_publisher_id
    )
