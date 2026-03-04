import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from cora.context import Context
from common.xml_utils import create_group, create_text


def create_origin_info(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    """
    Create an origin_info element
    """
    origin_info = create_group(
        "originInfo",
        [
            _create_date_issued(source_record),
            _create_agent(source_record, context),
            _create_place(source_record),
            _create_edition(source_record),
        ],
    )

    return origin_info


def _create_date_issued(source_record: ET.Element) -> ET.Element | None:
    """
    Create a date_issued element
    """
    return create_group(
        "dateIssued", [create_text("year", source_record.findtext("./dateIssued"))]
    )


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


def _create_agent_from_uncontrolled_publisher(publisher_name: str) -> ET.Element | None:
    return create_group(
        "agent",
        [
            create_text("namePart", publisher_name),
            create_group("role", [create_text("roleTerm", "pbl")]),
        ],
        repeatId="0",
    )


def _create_agent_from_controlled_publisher(
    publishing_house_id: str, context: Context
) -> ET.Element | None:
    cora_publisher_id = get_cora_id_by_old_id(
        publishing_house_id, record_type="diva-publisher", context=context
    )
    return create_group(
        "agent",
        [
            create_record_link("publisher", "diva-publisher", cora_publisher_id),
            create_group("role", [create_text("roleTerm", "pbl")]),
        ],
        repeatId="0",
    )


def _create_place(source_record: ET.Element) -> ET.Element | None:
    """
    Create a place element from publication/publisher/city
    """
    return create_group(
        "place",
        [create_text("placeTerm", source_record.findtext("./publisher/city"))],
        repeatId="0",
    )


def _create_edition(source_record: ET.Element) -> ET.Element | None:
    """
    Create an edition element from publication/edition
    """
    return create_text("edition", source_record.findtext("./edition"))
