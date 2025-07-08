import xml.etree.ElementTree as ET
from fedora_to_cora.create_classification_authority_ssif import (
    create_classification_authority_ssif,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_classification_authority_ssif():
    source_record = ET.fromstring(
        """
        <publication>
            <nationalCategories>
                <subject>
                    <subjectCode>30224</subjectCode>
                    <parents>
                        <subject>
                            <subjectCode>302</subjectCode>
                            <parents>
                                <subject>
                                    <subjectCode>3</subjectCode>
                                </subject>
                            </parents>    
                        </subject>
                    </parents>
                </subject>
                <subject>
                    <subjectCode>60301</subjectCode>
                    <parents>
                        <subject>
                            <subjectCode>603</subjectCode>
                            <parents>
                                <subject>
                                    <subjectCode>6</subjectCode>
                                </subject>
                            </parents>
                        </subject>
                    </parents>
                </subject>
                <subject>
                    <subjectCode>6</subjectCode>
                </subject>
            </nationalCategories>
        </publication>
        """
    )

    classifications = create_classification_authority_ssif(source_record)

    assert len(classifications) == 3

    assert_equal_for_xml_and_xml_string(
        classifications[0],
        """
        <classification authority="ssif" repeatId="0">
            30224
        </classification>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        classifications[1],
        """
        <classification authority="ssif" repeatId="1">
            60301
        </classification>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        classifications[2],
        """        
        <classification authority="ssif" repeatId="2">
            6
        </classification>
        """,
    )


def test_create_classification_authority_ssif_empty():
    source_record = ET.fromstring(
        """
        <publication>
            <nationalCategories>
            </nationalCategories>
        </publication>
        """
    )

    classifications = create_classification_authority_ssif(source_record)

    assert len(classifications) == 0
