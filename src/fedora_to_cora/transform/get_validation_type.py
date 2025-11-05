import xml.etree.ElementTree as ET

# publication_map = {
#     "50": "publication_journal-article",
#     "51": "publication_review-article",
#     "52": "publication_book-review",
#     "53": "publication_doctoral-thesis-compilation",
#     "54": "publication_doctoral-thesis-monograph",
#     "55": "publication_licentiate-thesis-compilation",
#     "56": "publication_licentiate-thesis-monograph",
#     "57": "publication_book",
#     "58": "publication_book-chapter",
#     "59": "conference_paper",
#     "60": "conference_proceeding",
#     "61": "intellectual-property_patent",
#     "62": "publication_report",
#     "63": "publication_edited-book",
#     "64": "publicationPreprintItem",
#     "65": "diva_degree-project",
#     "66": "publication_other",
#     "67": "diva_dissertation",
#     "71": "artistic-work_original-creative-work",
# }

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


def get_validation_type(
    publication_type_code: str | None, subtype_code: str | None
) -> str | None:
    if publication_type_code not in validation_type_mapping:
        return None

    publication_type_mapping = validation_type_mapping[publication_type_code]

    if subtype_code not in publication_type_mapping:
        return None

    return publication_type_mapping[subtype_code]


def get_validation_type_from_fedora_record(source_record: ET.Element) -> str | None:
    publication_type_code = source_record.findtext(
        "./publicationType/publicationTypeCode"
    )
    subtype_code = source_record.findtext("./subtype/publicationSubtypeCode")

    return get_validation_type(publication_type_code, subtype_code)
