import xml.etree.ElementTree as ET

import pytest
from fedora_to_cora.transform.create_note_type_publication_status import (
    create_note_type_publication_status,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


@pytest.mark.parametrize(
    "status_id, expected_status",
    [
        ("50", "accepted"),
        ("51", "inPress"),
        ("53", "published"),
        ("54", "submitted"),
        ("55", "aheadOfPrint"),
    ],
)
def test_creates_known_statuses(status_id, expected_status):
    source_record = ET.fromstring(
        f"""<publication>
                <publicationStatus>
                    <publicationStatusId>{status_id}</publicationStatusId>
                    <publicationStatusNames>
                    <publicationStatusName>
                        <publicationStatusNameId>161</publicationStatusNameId>
                        <locale>no</locale>
                        <publicationStatusName>Published</publicationStatusName>
                    </publicationStatusName>
                    <publicationStatusName>
                        <publicationStatusNameId>160</publicationStatusNameId>
                        <locale>en</locale>
                        <publicationStatusName>Published</publicationStatusName>
                    </publicationStatusName>
                    <publicationStatusName>
                        <publicationStatusNameId>159</publicationStatusNameId>
                        <locale>sv</locale>
                        <publicationStatusName>Published</publicationStatusName>
                    </publicationStatusName>
                    </publicationStatusNames>
                    <code>published</code>
                </publicationStatus>
            </publication>"""
    )
    note = create_note_type_publication_status(source_record)

    assert_equal_for_xml_and_xml_string(
        note, f"""<note type="publicationStatus">{expected_status}</note>"""
    )


def test_no_publication_status():
    source_record = ET.fromstring("""<publication></publication>""")
    note = create_note_type_publication_status(source_record)
    assert note is None


def test_unknown_publication_status():
    source_record = ET.fromstring(
        """<publication>
                <publicationStatus>
                    <publicationStatusId>9001</publicationStatusId>
                </publicationStatus>
            </publication>"""
    )
    note = create_note_type_publication_status(source_record)

    assert_equal_for_xml_and_xml_string(
        note,
        """<note type="publicationStatus">UNKNOWN PUBLICATION STATUS: 9001</note>""",
    )


def test_empty_publication_status():
    source_record = ET.fromstring(
        """<publication>
                <publicationStatus>
            </publicationStatus>
        </publication>"""
    )
    note = create_note_type_publication_status(source_record)

    assert note is None
