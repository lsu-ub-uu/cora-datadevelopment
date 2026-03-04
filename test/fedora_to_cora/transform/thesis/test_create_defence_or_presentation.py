from fedora_to_cora.transform.thesis.create_defence_or_presentation import (
    create_defence_or_presentation,
)
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_defence():
    source_record = ET.fromstring(
        """
         <publication>
            <publicationType>
                <publicationTypeId>54</publicationTypeId>
                <publicationTypeCode>monographDoctoralThesis</publicationTypeCode>
            </publicationType>
            <defence>
                <date>2022-07-31T16:19:00.000+02:00</date>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <room>
                    <name>Balsalen</name>
                    <street>Slottet</street>
                    <city>Uppsala</city>
                </room>
            </defence>
        </publication>

        """
    )

    admin = create_defence_or_presentation(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <defence>
                <language>
                    <languageTerm type="code" authority="iso639-2b">swe</languageTerm>
                </language>
                <dateOther type="presentation">
                    <year>2022</year>
                    <month>07</month>
                    <day>31</day>
                    <hh>16</hh>
                    <mm>19</mm>
                </dateOther>
                <address>
                    <location>
                        Balsalen
                    </location>
                    <street>Slottet</street>
                    <city>
                        Uppsala
                    </city>
                </address>
            </defence>
        """,
    )


def test_create_empty_defence():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>54</publicationTypeId>
                <publicationTypeCode>monographDoctoralThesis</publicationTypeCode>
            </publicationType>
            <defence>
                <room>
                </room>
            </defence>
        </publication>
        """
    )

    admin = create_defence_or_presentation(source_record)

    assert admin is None


def test_create_empty_presentation():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>65</publicationTypeId>
                <publicationTypeCode>studentThesis</publicationTypeCode>
            </publicationType>
            <defence>
                <room>
                </room>
            </defence>
        </publication>
        """
    )

    admin = create_defence_or_presentation(source_record)

    assert admin is None


def test_create_presentation_if_degree_project():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>65</publicationTypeId>
                <publicationTypeCode>studentThesis</publicationTypeCode>
            </publicationType>
            <defence>
                <date>2022-07-31T16:19:00.000+02:00</date>
                <language>
                    <languageCode3>swe</languageCode3>
                </language>
                <room>
                    <name>Balsalen</name>
                    <street>Slottet</street>
                    <city>Uppsala</city>
                </room>
            </defence>
        </publication>
        """
    )

    admin = create_defence_or_presentation(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <presentation>
                <language>
                    <languageTerm type="code" authority="iso639-2b">swe</languageTerm>
                </language> 
                <dateOther type="presentation">
                    <year>2022</year>
                    <month>07</month>
                    <day>31</day>
                    <hh>16</hh>
                    <mm>19</mm>
                </dateOther>
                <address>
                    <location>
                        Balsalen
                    </location>
                    <street>Slottet</street>
                    <city>
                        Uppsala
                    </city>
                </address>
            </presentation>
        """,
    )
