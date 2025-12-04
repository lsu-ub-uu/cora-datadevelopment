import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.related_items.create_proceeding import (
    create_related_item_type_proceeding,
)


def test_no_conference():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    conference = create_related_item_type_proceeding(source_record)

    assert conference is None


def test_empty_conference():
    source_record = ET.fromstring(
        """
        <publication>
            <conference></conference>
        </publication>
        """
    )

    conference = create_related_item_type_proceeding(source_record)

    assert conference is None


def test_create_related_item_type_conference_with_title():
    source_record = ET.fromstring(
        """
        <publication>
            <conference>En fiktiv konferens</conference>
        </publication>
        """
    )

    conference = create_related_item_type_proceeding(source_record)

    assert_equal_for_xml_and_xml_string(
        conference,
        """
        <relatedItem type="proceeding">
            <proceeding>En fiktiv konferens</proceeding>
        </relatedItem>
        """,
    )
