import pytest
import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_validation_type_by_publication_type_id import (
    get_validation_type_by_publication_type_id,
    get_validation_type_from_fedora_record,
)


@pytest.mark.parametrize(
    "pub_type_id,expected",
    [
        ("50", "publication_journal-article"),
        ("51", "publication_review-article"),
        ("52", "publication_book-review"),
        ("53", "publication_doctoral-thesis-compilation"),
        ("54", "publication_doctoral-thesis-monograph"),
        ("55", "publication_licentiate-thesis-compilation"),
        ("56", "publication_licentiate-thesis-monograph"),
        ("57", "publication_book"),
        ("58", "publication_book-chapter"),
        ("59", "conference_paper"),
        ("60", "conference_proceeding"),
        ("61", "intellectual-property_patent"),
        ("62", "publication_report"),
        ("63", "publication_edited-book"),
        ("64", "publicationPreprintItem"),
        ("65", "diva_degree-project"),
        ("66", "publication_other"),
        ("67", "diva_dissertation"),
        ("71", "artistic-work_original-creative-work"),
    ],
)
def test_known_publication_type_ids(pub_type_id, expected):
    assert get_validation_type_by_publication_type_id(pub_type_id) == expected


@pytest.mark.parametrize("invalid_id", ["999", "", None])
def test_unknown_publication_type_id_raises_keyerror(invalid_id):
    with pytest.raises(KeyError):
        get_validation_type_by_publication_type_id(invalid_id)


def test_get_validation_type():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
            </publicationType>
        </publication>
        """
    )

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "publication_edited-book"


def test_missing_validation_type():
    source_record = ET.fromstring(
        f"""
        <publication>
            <publicationType>
            </publicationType>
        </publication>
        """
    )

    with pytest.raises(KeyError):
        get_validation_type_from_fedora_record(source_record)
