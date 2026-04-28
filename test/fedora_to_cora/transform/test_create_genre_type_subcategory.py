import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_genre_type_subcategory import (
    create_genre_type_subcategory,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_no_subtype():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)

    assert genre_type_subcategory is None


def test_policy_document():
    source_record = ET.fromstring(
        """
        <publication>
            <subtype>
                <publicationSubtypeId>2</publicationSubtypeId>
                <publicationSubtypeCode>policyDocument</publicationSubtypeCode>
            </subtype>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)
    assert_equal_for_xml_and_xml_string(
        genre_type_subcategory,
        """
        <genre type="subcategory">policyDocument</genre>
        """,
    )


def test_exhibition_catalog():
    source_record = ET.fromstring(
        """
        <publication>
            <subtype>
                <publicationSubtypeId>3</publicationSubtypeId>
                <publicationSubtypeCode>exhibitionCatalogue</publicationSubtypeCode>
            </subtype>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)
    assert_equal_for_xml_and_xml_string(
        genre_type_subcategory,
        """
        <genre type="subcategory">exhibitionCatalog</genre>
        """,
    )


def test_oral_presentation():
    source_record = ET.fromstring(
        """
        <publication>
            <subtype>
                <publicationSubtypeId>3</publicationSubtypeId>
                <publicationSubtypeCode>presentation</publicationSubtypeCode>
            </subtype>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)
    assert_equal_for_xml_and_xml_string(
        genre_type_subcategory,
        """
        <genre type="subcategory">oralPresentation</genre>
        """,
    )


def test_oral_presentation_abstract():
    source_record = ET.fromstring(
        """
        <publication>
            <subtype>
                <publicationSubtypeId>3</publicationSubtypeId>
                <publicationSubtypeCode>abstracts</publicationSubtypeCode>
            </subtype>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)
    assert_equal_for_xml_and_xml_string(
        genre_type_subcategory,
        """
        <genre type="subcategory">oralPresentationAbstract</genre>
        """,
    )


def test_other_subtype():
    source_record = ET.fromstring(
        """
        <publication>
            <subtype>
                <publicationSubtypeId>53</publicationSubtypeId>
                <publicationSubtypeCode>newsItem</publicationSubtypeCode>
            </subtype>
        </publication>
        """
    )

    genre_type_subcategory = create_genre_type_subcategory(source_record)

    assert genre_type_subcategory is None
