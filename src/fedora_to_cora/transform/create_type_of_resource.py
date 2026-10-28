import xml.etree.ElementTree as ET

from common.xml_utils import create_text

# DB table mediatype
map_media_type = {
    "still image": "stillImage",  # 1
    "three dimensional object": "artifact",  # 2
    "sound recording": "soundRecording",  # 3
    "notated music": "notatedMusic",  # 4
    "software, multimedia": "softwareMultimedia",  # 5
    "moving image": "movingImage",  # 6
    "mixed material": "mixedMaterial",  # 7
    "sound recording-musical": "soundRecordingMusical",  # 8
    "sound recording-nonmusical": "soundRecordingNonMusical",  # 9
    "text": "text",  # 10
    "cartographic": "cartographic",  # 11
}


def create_type_of_resource(source_record: ET.Element) -> ET.Element | None:
    media_type_code = source_record.findtext("./mediaType/code")
    publication_type_code = source_record.findtext(
        "./publicationType/publicationTypeCode"
    )
    assert publication_type_code is not None

    if media_type_code is None:
        return None

    if _should_ignore_media_type(media_type_code, publication_type_code):
        return None

    return create_text(
        "typeOfResource",
        value=_get_type_of_resource_by_media_type(media_type_code),
    )


def _get_type_of_resource_by_media_type(media_type_code: str) -> str:
    """
    Returns the Cora DiVA typeOfResource based on the DiVA Clic publication type ID.

    :param media_type: The ID of the publication type.
    :return: The typeOfResource as a string.
    :raises KeyError: If the media_type is not found.
    """
    if media_type_code not in map_media_type:
        raise KeyError(f"Unknown media_type: {media_type_code}")
    return map_media_type[media_type_code]


def _should_ignore_media_type(media_type_code: str, publication_type_code: str) -> bool:
    """
    Determines if the given media type and publication type code should be ignored for validation.

    :param media_type: The ID of the media type.
    :param publication_type_code: The publication type code.
    :return: True if the combination should be ignored, False otherwise.
    """
    return media_type_code == "text" and publication_type_code not in [
        "other",
        "artisticOutput",
    ]
