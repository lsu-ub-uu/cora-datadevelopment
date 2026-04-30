import pytest
import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_validation_type import (
    _get_validation_type,
    get_validation_type_from_fedora_record,
)


@pytest.mark.parametrize(
    "pub_type_code, subtype_code, expected",
    [
        ("article", None, "publication_journal-article"),
        ("article", "meetingAbstract", "publication_editorial-letter"),
        ("article", "editorialMaterial", "publication_editorial-letter"),
        ("article", "letter", "publication_editorial-letter"),
        ("article", "newsItem", "publication_newspaper-article"),
        ("review", None, "publication_review-article"),
        ("bookReview", None, "publication_book-review"),
        (
            "comprehensiveDoctoralThesis",
            None,
            "publication_doctoral-thesis-compilation",
        ),
        ("monographDoctoralThesis", None, "publication_doctoral-thesis-monograph"),
        (
            "comprehensiveLicentiateThesis",
            None,
            "publication_licentiate-thesis-compilation",
        ),
        (
            "monographLicentiateThesis",
            None,
            "publication_licentiate-thesis-monograph",
        ),
        ("book", None, "publication_book"),
        ("chapter", None, "publication_book-chapter"),
        ("conferencePaper", None, "conference_paper"),
        ("conferencePaper", "publishedPaper", "conference_paper"),
        ("conferencePaper", "abstracts", "conference_other"),
        ("conferencePaper", "poster", "conference_poster"),
        ("conferencePaper", "presentation", "conference_other"),
        ("conferenceProceedings", None, "conference_proceeding"),
        ("patent", None, "intellectual-property_patent"),
        ("report", None, "publication_report"),
        ("collection", None, "publication_edited-book"),
        ("manuscript", None, "publication_preprint"),
        ("studentThesis", None, "diva_degree-project"),
        ("other", None, "publication_other"),
        ("other", "policyDocument", "publication_other"),
        ("other", "exhibitionCatalogue", "publication_other"),
        ("dissertation", None, "diva_dissertation"),
        ("dataset", None, None),
        ("dataset", "primaryData", None),
        ("dataset", "aggregatedData", None),
        ("artisticOutput", None, "artistic-work_original-creative-work"),
    ],
)
def test_known_publication_type_ids(pub_type_code, subtype_code, expected):
    assert _get_validation_type(pub_type_code, subtype_code) == expected


@pytest.mark.parametrize("invalid_id", ["999", "", None])
def test_unknown_publication_type_returns_none(invalid_id):
    validation_type = _get_validation_type(invalid_id, subtype_code=None)
    assert validation_type is None


def test_known_publication_type_with_unknown_subtype_returns_none():
    validation_type = _get_validation_type("article", "unknownSubtype")
    assert validation_type is None


def test_get_validation_type():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "publication_edited-book"


def test_get_validation_type_with_subtype():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>50</publicationTypeId>
                <publicationTypeCode>article</publicationTypeCode>
            </publicationType>
            <subtype>
                <publicationSubtypeId>53</publicationSubtypeId>
                <publicationSubtypeCode>newsItem</publicationSubtypeCode>
            </subtype>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "publication_newspaper-article"


def test_empty_subtype():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>50</publicationTypeId>
                <publicationTypeCode>article</publicationTypeCode>
            </publicationType>
            <subtype>
                <publicationSubtypeNames />
            </subtype>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "publication_journal-article"


def test_missing_validation_type():
    source_record = ET.fromstring(f"""
        <publication>
            <publicationType>
            </publicationType>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) is None


def test_handle_publication_subtype_from_root_element():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>50</publicationTypeId>
                <publicationTypeCode>article</publicationTypeCode>
            </publicationType>
            <publicationSubtype>editorialMaterial</publicationSubtype>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "publication_editorial-letter"


@pytest.mark.parametrize(
    "host_publication_type",
    ["comprehensiveDoctoralThesis", "comprehensiveLicentiateThesis"],
)
def test_returns_diva_manuscript_for_manuscript_that_is_part_of_thesis(
    host_publication_type,
):
    source_record = ET.fromstring(f"""
        <publication>
            <publicationType>
                <publicationTypeCode>manuscript</publicationTypeCode>
            </publicationType>
            <hostPublications>
                <hostPublication>
                    <publicationType>
                        <publicationTypeCode>someOtherHostPublicationType</publicationTypeCode>
                    </publicationType>
                </hostPublication>   
                <hostPublication>
                    <publicationType>
                        <publicationTypeCode>{host_publication_type}</publicationTypeCode>
                    </publicationType>
                </hostPublication>   
            </hostPublications>
        </publication>
        """)

    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (validation_type) == "diva_manuscript"
