from fedora_to_cora.transform.create_type_of_resource import create_type_of_resource
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET
import pytest


@pytest.mark.parametrize(
    "media_type,expected",
    [
        ("1", "stillImage"),
        ("2", "artifact"),
        ("3", "soundRecording"),
        ("4", "notatedMusic"),
        ("6", "movingImage"),
        ("7", "mixedMaterial"),
        ("5", "softwareMultimedia"),
        ("8", "soundRecordingMusical"),
        ("9", "soundRecordingNonMusical"),
        ("10", "text"),
        ("11", "cartographic"),
    ],
)
def test_create_type_of_resource(media_type, expected):
    source_record = ET.fromstring(
        f"""
        <publication>
            <mediaType>
                <autoId>{media_type}</autoId>
            </mediaType>
        </publication>
        """
    )

    type_of_resource = create_type_of_resource(source_record)

    assert_equal_for_xml_and_xml_string(
        type_of_resource,
        f"""
        <typeOfResource>{expected}</typeOfResource>
        """,
    )


def test_missing_media_type():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    type_of_resource = create_type_of_resource(source_record)

    assert type_of_resource is None


def test_wrong_media_type():
    source_record = ET.fromstring(
        f"""
        <publication>
            <mediaType>
                <autoId>999</autoId>
            </mediaType>
        </publication>
        """
    )

    with pytest.raises(KeyError):
        create_type_of_resource(source_record)
