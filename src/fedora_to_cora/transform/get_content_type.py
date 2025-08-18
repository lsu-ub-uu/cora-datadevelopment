content_type_map = {
    "refereed": "ref",
    "science": "vet",
    "other": "pop",
}


def get_content_type(content_type_code):
    """
    Returns the DiVA content type based on the DiVA Classic content type code.
    
    :param content_type_code: The Code of the publication type.
    :return: The validation type as a string.
    :raises KeyError: If the content_type_code is not found.
    """
    if content_type_code not in content_type_map:
        raise KeyError(f"Unknown content_type_code: {content_type_code}")
    return content_type_map[content_type_code]