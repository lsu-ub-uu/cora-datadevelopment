from xml.etree import ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.patent.create_patent_country import create_patent_country


def test_create_patent_country():
    source_record = ET.fromstring(
        """
    <record>
        <patentCountry>
            <countryCode>au</countryCode>
            <countryNames>
            <countryName>
                <countryNameId>10363</countryNameId>
                <locale>no</locale>
                <countryName>Australia</countryName>
            </countryName>
            <countryName>
                <countryNameId>426</countryNameId>
                <locale>en</locale>
                <countryName>Australia</countryName>
            </countryName>
            <countryName>
                <countryNameId>427</countryNameId>
                <locale>sv</locale>
                <countryName>Australien</countryName>
            </countryName>
            </countryNames>
            <showsOnList>true</showsOnList>
        </patentCountry>
    </record>
    """
    )
    patent_country = create_patent_country(source_record)

    assert_equal_for_xml_and_xml_string(
        patent_country, """<patentCountry>au</patentCountry>"""
    )


def test_empty_patent_country():
    source_xml = ET.fromstring(
        """
        <publication>
            <patentCountry>
            <countryNames />
            <showsOnList>false</showsOnList>
        </patentCountry>
        </publication>
    """
    )

    patent_country = create_patent_country(source_xml)

    assert patent_country is None
