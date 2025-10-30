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
    append_if_value(origin_info, _create_place(source_record))
    append_if_value(origin_info, _create_edition(source_record))

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

    publishing_house_id = publisher.findtext("./publishingHouse/publishingHouseId")
    if publishing_house_id is not None:
        return _create_agent_from_controlled_publisher(publishing_house_id, context)

    publisher_name = publisher.findtext("./publisherName")
    if publisher_name is not None:
        return _create_agent_from_uncontrolled_publisher(publisher_name)


def _create_agent_from_uncontrolled_publisher(publisher_name: str) -> ET.Element:
    agent = ET.Element("agent", repeatId="0")
    ET.SubElement(agent, "namePart").text = publisher_name

    role = ET.SubElement(agent, "role")
    ET.SubElement(role, "roleTerm").text = "pbl"

    return agent


def _create_agent_from_controlled_publisher(
    publishing_house_id: str, context: Context
) -> ET.Element | None:
    agent = ET.Element("agent", repeatId="0")
    cora_publisher_id = get_cora_id_by_old_id(
        publishing_house_id, record_type="diva-publisher", context=context
    )
    link = create_record_link_using_name_type_id(
        "publisher", "diva-publisher", cora_publisher_id
    )
    agent.append(link)

    role = ET.SubElement(agent, "role")
    ET.SubElement(role, "roleTerm").text = "pbl"

    return agent


def _create_place(source_record: ET.Element) -> ET.Element | None:
    """
    Create a place element from publication/publisher/city
    """
    city = source_record.find("./publisher/city")
    if city is None or city.text is None:
        return None

    place = ET.Element("place", repeatId="0")
    ET.SubElement(place, "placeTerm").text = city.text
    return place


def _create_edition(source_record: ET.Element) -> ET.Element | None:
    """
    Create an edition element from publication/edition
    """
    edition = source_record.find("./edition")
    if edition is None or edition.text is None:
        return None

    edition_element = ET.Element("edition")
    edition_element.text = edition.text
    return edition_element
