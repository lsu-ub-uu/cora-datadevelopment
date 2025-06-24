import xml.etree.ElementTree as ET
from fedora_to_cora import create_note_type_creator_count
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_note_type_creator_count():
    source_record = ET.fromstring(
        """
        <publication>
           <noOfContributors>32</noOfContributors>
        </publication>
        """
    )

    creator_count = create_note_type_creator_count(source_record)

    assert_equal_for_xml_and_xml_string(
        creator_count,
        """
        <note type="creatorCount">32</note>
        """,
    )


def test_no_of_contributors_missing():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    creator_count = create_note_type_creator_count(source_record)

    assert creator_count is None
