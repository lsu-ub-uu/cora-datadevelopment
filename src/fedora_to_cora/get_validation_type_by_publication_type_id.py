publication_map = {
    "50": "publication_journal-article",
    "51": "publication_review-article",
    "52": "publication_book-review",
    "53": "publication_doctoral-thesis-compilation", 
    "54": "publication_doctoral-thesis-monograph",
    "55": "publication_licentiate-thesis-compilation",
    "56": "publication_licentiate-thesis-monograph",
    "57": "publication_book",
    "58": "publication_book-chapter",
    "59": "conference_paper", 
    "60": "conference_proceeding",
    "61": "intellectual-property_patent",
    "62": "publication_report", 
    "63": "publication_edited-book",
    "64": "publicationPreprintItem",
    "65": "diva_degree-project",
    "66": "publication_other",
    "67": "diva_dissertation",
    "71": "artistic-work_original-creative-work"
}


def get_validation_type_by_publication_type_id(publication_type_id):
    """
    Returns the Cora DiVA validation type based on the DiVA Classic publication type ID.
    
    :param publication_type_id: The ID of the publication type.
    :return: The validation type as a string.
    :raises KeyError: If the publication_type_id is not found.
    """
    if publication_type_id not in publication_map:
        raise KeyError(f"Unknown publication_type_id: {publication_type_id}")
    return publication_map[publication_type_id]