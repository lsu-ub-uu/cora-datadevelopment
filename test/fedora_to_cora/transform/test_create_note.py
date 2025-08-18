from fedora_to_cora.transform.create_note import create_note
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET


def test_create_note():
    source_record = ET.fromstring(
        """
        <publication>
            <someSourceTag>En anmärkning</someSourceTag>
        </publication>
        """
    )

    note = create_note(
        source_record, type="someType", source_selector="./someSourceTag"
    )

    assert_equal_for_xml_and_xml_string(
        note,
        """
        <note type="someType">En anmärkning</note>
        """,
    )


def test_create_note_without_text():
    source_record = ET.fromstring(
        """
        <publication>
            <someSourceTag></someSourceTag>
        </publication>
        """
    )

    note = create_note(
        source_record, type="someType", source_selector="./someSourceTag"
    )

    assert_equal_for_xml_and_xml_string(
        note,
        """
        <note type="someType"></note>
        """,
    )


def test_no_of_contributors_missing():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    note = create_note(
        source_record, type="someType", source_selector="./someSourceTag"
    )

    assert_equal_for_xml_and_xml_string(
        note,
        """
        <note type="someType"></note>
        """,
    )
