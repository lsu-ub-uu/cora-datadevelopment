import xml.etree.ElementTree as ET

# Mapping from publicationTypeCode and publicationSubtypeCode to Cora validationType.
validation_type_mapping = {
    "article": {
        None: "publication_journal-article",
        "meetingAbstract": "publication_editorial-letter",
        "editorialMaterial": "publication_editorial-letter",
        "letter": "publication_editorial-letter",
        "newsItem": "publication_newspaper-article",
    },
    "review": {
        None: "publication_review-article",
    },
    "bookReview": {
        None: "publication_book-review",
    },
    "comprehensiveDoctoralThesis": {
        None: "publication_doctoral-thesis-compilation",
    },
    "monographDoctoralThesis": {
        None: "publication_doctoral-thesis-monograph",
    },
    "comprehensiveLicentiateThesis": {
        None: "publication_licentiate-thesis-compilation",
    },
    "monographLicentiateThesis": {
        None: "publication_licentiate-thesis-monograph",
    },
    "book": {
        None: "publication_book",
    },
    "chapter": {
        None: "publication_book-chapter",
    },
    "conferencePaper": {
        None: "conference_paper",
        "publishedPaper": "conference_paper",
        "abstracts": "conference_other",
        "poster": "conference_poster",
        "presentation": "conference_other",
    },
    "conferenceProceedings": {
        None: "conference_proceeding",
    },
    "patent": {
        None: "intellectual-property_patent",
    },
    "report": {
        None: "publication_report",
    },
    "collection": {
        None: "publication_edited-book",
    },
    "manuscript": {
        None: "publication_preprint",
    },
    "studentThesis": {
        None: "diva_degree-project",
    },
    "other": {
        None: "publication_other",
        "policyDocument": "publication_other",
        "exhibitionCatalogue": "publication_other",
    },
    "dissertation": {
        None: "diva_dissertation",
    },
    "dataset": {
        None: None,
        "primaryData": None,
        "aggregatedData": None,
    },
    "artisticOutput": {
        None: "artistic-work_original-creative-work",
    },
}


def get_validation_type_from_fedora_record(source_record: ET.Element) -> str | None:
    publication_type_code = source_record.findtext(
        "./publicationType/publicationTypeCode"
    )

    if publication_type_code == "manuscript":
        return _get_validation_type_for_manuscript(source_record)

    publication_subtype_code = _get_publication_subtype_code(source_record)

    return _get_validation_type(publication_type_code, publication_subtype_code)


def _get_validation_type(
    publication_type_code: str | None, subtype_code: str | None
) -> str | None:
    if publication_type_code not in validation_type_mapping:
        return None

    publication_type_mapping = validation_type_mapping[publication_type_code]

    if subtype_code not in publication_type_mapping:
        return None

    return publication_type_mapping[subtype_code]


def _get_publication_subtype_code(source_record: ET.Element) -> str | None:
    subtype_code = source_record.findtext("./subtype/publicationSubtypeCode")
    if subtype_code is not None:
        return subtype_code

    # In some cases, the publication subtype might be stored directly under publicationSubtype instead of subtype/publicationSubtypeCode.
    return source_record.findtext("./publicationSubtype")


def _get_validation_type_for_manuscript(source_record: ET.Element) -> str | None:
    # For manuscripts, we need to check if it's part of a thesis to determine if it is a manuscript or preprint.
    host_publication_types = source_record.findall(
        "./hostPublications/hostPublication/publicationType/publicationTypeCode"
    )

    if _is_part_of_thesis(source_record):
        return "diva_manuscript"

    return "publication_preprint"


def _is_part_of_thesis(source_record: ET.Element) -> bool:
    host_publication_type_codes = source_record.findall(
        "./hostPublications/hostPublication/publicationType/publicationTypeCode"
    )
    thesis_types = {"comprehensiveDoctoralThesis", "comprehensiveLicentiateThesis"}

    return any(h.text in thesis_types for h in host_publication_type_codes)
