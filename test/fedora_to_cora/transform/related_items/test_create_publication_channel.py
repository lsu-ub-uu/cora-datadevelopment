import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.related_items.create_publication_channel import (
    create_publication_channel,
)


def test_create_publication_channel():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationChannel>Journal of Testing</publicationChannel>
        </publication>
        """
    )

    publication_channel = create_publication_channel(source_record)

    assert_equal_for_xml_and_xml_string(
        publication_channel,
        """
        <relatedItem type="publicationChannel">
            <publicationChannel>Journal of Testing</publicationChannel>
        </relatedItem>
        """,
    )


def test_empty_publication_channel():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationChannel></publicationChannel>
        </publication>
        """
    )

    publication_channel = create_publication_channel(source_record)

    assert publication_channel is None


def test_missing_publication_channel():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    publication_channel = create_publication_channel(source_record)

    assert publication_channel is None
