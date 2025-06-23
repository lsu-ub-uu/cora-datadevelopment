import pytest
from xml.etree import ElementTree as ET
from fedora_to_cora import create_genre_type_output_type
from common.test_helper import assert_equal_for_xml_and_xml_string


source_record = ET.fromstring(
    """
    <publication>
        <publicationType>
            <publicationTypeId>53</publicationTypeId>
            <publicationTypeCode>comprehensiveDoctoralThesis</publicationTypeCode>
        </publicationType>
    </publication>
"""
)


def test_create_genre_type_output_type():
    genre = create_genre_type_output_type(source_record)

    assert_equal_for_xml_and_xml_string(
        genre,
        """<genre type="outputType">publication_doctoral-thesis-compilation</genre>""",
    )


def test_create_genre_type_output_type_missing():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )
    pytest.raises(
        AssertionError,
        create_genre_type_output_type,
        source_record,
    )
