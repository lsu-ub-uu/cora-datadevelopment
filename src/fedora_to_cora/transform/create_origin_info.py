import xml.etree.ElementTree as ET
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from common.common_data import create_record_link
from cora.context import Context
from common.xml_utils import create_group, create_text
from fedora_to_cora.utils import (
    is_part_of_book,
)


def create_origin_info(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    return create_group(
        "originInfo",
        [
            _create_date_issued(source_record),
            (
                create_publisher(source_record, context)
                if not is_part_of_book(source_record)
                else None
            ),
        ],
    )


def _create_date_issued(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "dateIssued", [create_text("year", source_record.findtext("./dateIssued"))]
    )


def create_publisher(source_record: ET.Element, context: Context) -> ET.Element | None:
    publisher = source_record.find("./publisher")

    if publisher is None:
        return None

    city = publisher.findtext("./city")

    publishing_house_id = publisher.findtext("./publishingHouse/publishingHouseId")
    if publishing_house_id is not None:
        return _create_controlled_publisher(publishing_house_id, city, context)

    publisher_name = publisher.findtext("./publisherName")
    if publisher_name is not None:
        return _create_uncontrolled_publisher(publisher_name, city)


def _create_uncontrolled_publisher(
    publisher_name: str, city: str | None
) -> ET.Element | None:
    return create_group(
        "name",
        type="corporate",
        otherType="publisher",
        repeatId="0",
        children=[
            create_text("namePart", type="publisher", value=publisher_name),
            create_group("place", [create_text("placeTerm", city)]),
            create_group("role", [create_text("roleTerm", "pbl")]),
        ],
    )


def _create_controlled_publisher(
    publishing_house_id: str, city: str | None, context: Context
) -> ET.Element | None:
    cora_publisher_id = get_cora_id_by_old_id(
        publishing_house_id, record_type="diva-publisher", context=context
    )
    return create_group(
        "name",
        type="corporate",
        otherType="publisher",
        repeatId="0",
        children=[
            create_record_link("publisher", "diva-publisher", cora_publisher_id),
            create_group("place", [create_text("placeTerm", city)]),
            create_group("role", [create_text("roleTerm", "pbl")]),
        ],
    )
