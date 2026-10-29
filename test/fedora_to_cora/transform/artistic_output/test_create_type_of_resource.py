from fedora_to_cora.transform.create_type_of_resource import create_type_of_resource
from common.test_helper import assert_equal_for_xml_and_xml_string
import xml.etree.ElementTree as ET
import pytest


@pytest.mark.parametrize(
    "media_type_code,expected_type_of_resource",
    [
        ("still image", "stillImage"),
        ("three dimensional object", "artifact"),
        ("sound recording", "soundRecording"),
        ("notated music", "notatedMusic"),
        ("software, multimedia", "softwareMultimedia"),
        ("moving image", "movingImage"),
        ("mixed material", "mixedMaterial"),
        ("sound recording-musical", "soundRecordingMusical"),
        ("sound recording-nonmusical", "soundRecordingNonMusical"),
        ("text", "text"),
        ("cartographic", "cartographic"),
    ],
)
def test_create_type_of_resource(media_type_code, expected_type_of_resource):
    source_record = ET.fromstring(f"""
        <publication>
            <publicationType>
                <publicationTypeCode>artisticOutput</publicationTypeCode>
            </publicationType>
            <mediaType>
                <code>{media_type_code}</code>
            </mediaType>
        </publication>
        """)

    type_of_resource = create_type_of_resource(source_record)

    assert_equal_for_xml_and_xml_string(
        type_of_resource,
        f"""
        <typeOfResource>{expected_type_of_resource}</typeOfResource>
        """,
    )


def test_missing_media_type():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeCode>publication_journal-article</publicationTypeCode>
            </publicationType>
        </publication>
        """)

    type_of_resource = create_type_of_resource(source_record)

    assert type_of_resource is None


def test_wrong_media_type():
    source_record = ET.fromstring(f"""
        <publication>
            <publicationType>
                <publicationTypeCode>publication_journal-article</publicationTypeCode>
            </publicationType>
            <mediaType>
                <code>wrong</code>
            </mediaType>
        </publication>
        """)

    with pytest.raises(KeyError):
        create_type_of_resource(source_record)


@pytest.mark.parametrize(
    "publication_type_code,should_skip_text",
    [
        ("article", True),
        ("review", True),
        ("bookReview", True),
        ("comprehensiveDoctoralThesis", True),
        ("monographDoctoralThesis", True),
        ("comprehensiveLicentiateThesis", True),
        ("monographLicentiateThesis", True),
        ("book", True),
        ("chapter", True),
        ("conferencePaper", True),
        ("conferenceProceedings", True),
        ("patent", True),
        ("report", True),
        ("collection", True),
        ("manuscript", True),
        ("studentThesis", True),
        ("dissertation", True),
        ("other", False),
        ("artisticOutput", False),
    ],
)
def test_ignore_type_of_resource_of_type_text_for_validation_types_that_are_implicitly_text(
    publication_type_code, should_skip_text
):
    source_record = ET.fromstring(f"""
        <publication>
            <publicationType>
                <publicationTypeCode>{publication_type_code}</publicationTypeCode>
            </publicationType>
            <mediaType>
                <code>text</code>
            </mediaType>
        </publication>
        """)

    type_of_resource = create_type_of_resource(source_record)

    if should_skip_text:
        assert type_of_resource is None
    else:
        assert_equal_for_xml_and_xml_string(
            type_of_resource,
            f"""
                <typeOfResource>text</typeOfResource>
                """,
        )
