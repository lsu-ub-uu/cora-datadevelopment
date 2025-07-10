from fedora_to_cora.thesis.create_defence import create_defence
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_defence():
    source_record = ET.fromstring(
        """
        <publication>
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
                <grantingInstitution>
                    <organisationId>978</organisationId>
                    <organisationName>
                        <name>Uppsala universitet</name>
                    </organisationName>
                    <organisationAddress>
                        <addressId>1956</addressId>
                        <postnumber>75105</postnumber>
                        <city>Uppsala</city>
                        <country>
                            <countryCode>se</countryCode>
                        </country>
                    </organisationAddress>
                </grantingInstitution>
            </defence>
        </publication>
        """
    )

    admin = create_defence(source_record)

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
                <location>
                    Balsalen
                </location>
                <address>Slottet, 75105, Uppsala, se</address>
                <place>
                    <placeTerm>
                    Uppsala
                    </placeTerm>
                </place>
            </defence>
        """,
    )
