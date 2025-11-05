import pytest
import xml.etree.ElementTree as ET
from fedora_to_cora.utils import is_part_of_book, is_part_of_conference


def test_is_part_of_book_true():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>chapter</publicationTypeCode>
            </publicationType>
        </publication>
        """
    )

    assert is_part_of_book(source_record) is True


def test_is_part_of_book_false():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>monograph</publicationTypeCode>
            </publicationType>
        </publication>
        """
    )

    assert is_part_of_book(source_record) is False


def test_is_part_of_conference_true():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>conferencePaper</publicationTypeCode>
            </publicationType>
        </publication>
        """
    )

    assert is_part_of_conference(source_record) is True


def test_is_part_of_conference_false():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>proceedings</publicationTypeCode>
            </publicationType>
        </publication>
        """
    )

    assert is_part_of_conference(source_record) is False
