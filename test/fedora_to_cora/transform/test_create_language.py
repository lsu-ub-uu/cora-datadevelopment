import xml.etree.ElementTree as ET

import pytest
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_language import create_language


def test_create_language():
    source_record = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <language>
                    <languageCode3>eng</languageCode3>
                </language>
            </originalPublicationTitle>
        </publication>
        """
    )

    language = create_language(source_record)

    assert_equal_for_xml_and_xml_string(
        language,
        """
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        """,
    )


def test_create_language_missing_language():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    language = create_language(source_record)

    assert language is None
