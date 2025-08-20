import xml.etree.ElementTree as ET

map_media_type = {
    "1": "stillImage",  # still image
    "2": "artifact",  # three dimensional object
    "3": "soundRecording",  # sound recording
    "4": "notatedMusic",  # notated music
    "6": "movingImage",  # moving image
    "7": "mixedMaterial",  # mixed material
    "5": "softwareMultimedia",  # software, multimedia
    "8": "soundRecordingMusical",  # sound recording-musical
    "9": "soundRecordingNonMusical",  # sound recording-nonmusical
    "10": "text",  # text
    "11": "cartographic",  # cartographic
}


def create_type_of_resource(source_record: ET.Element) -> ET.Element:
    type_of_resource = ET.Element("typeOfResource")
    media_type = source_record.findtext("./mediaType/autoId")
    if media_type is not None:
        type_of_resource.text = _get_type_of_resource_by_media_type(media_type)

    return type_of_resource


def _get_type_of_resource_by_media_type(media_type: str) -> str:
    """
    Returns the Cora DiVA typeOfResource based on the DiVA Clic publication type ID.

    :param media_type: The ID of the publication type.
    :return: The typeOfResource as a string.
    :raises KeyError: If the media_type is not found.
    """
    if media_type not in map_media_type:
        raise KeyError(f"Unknown media_type: {media_type}")
    return map_media_type[media_type]
