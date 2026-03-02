import xml.etree.ElementTree as ET

import pytest
from db_to_cora.funder_transform import transform_funder
from common.test_helper import assert_equal_for_xml_and_xml_string
from common.xml_validate import XMLValidationError


def test_required_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <name_swe>Ett namn</name_swe>
        </DATA_RECORD>       
        """
    )

    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <authority lang="swe" repeatId="swe">
            <name type="corporate">
                <namePart>Ett namn</namePart>
            </name>
        </authority>
    </funder>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_without_name():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
        </DATA_RECORD>       
        """
    )

    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
    </funder>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_with_with_empty_tag():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>65</old_id>
            <name_swe>Ecosystem dynamics in the Baltic Sea in a changing climate perspective - ECOCHANGE</name_swe>
            <name_eng></name_eng>
            <end_date></end_date>
            <identifier_organisationNumber></identifier_organisationNumber>
            <identifier_doi></identifier_doi>
            <locale_swe>sv</locale_swe>
            <locale_eng></locale_eng>
            <funder_name_id></funder_name_id>
        </DATA_RECORD>    
        """
    )

    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
            <linkedRecordType>validationType</linkedRecordType>
            <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
            <linkedRecordType>system</linkedRecordType>
            <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>65</oldId>
        </recordInfo>
        <authority lang="swe" repeatId="swe">
            <name type="corporate">
            <namePart>Ecosystem dynamics in the Baltic Sea in a changing climate perspective - ECOCHANGE</namePart>
            </name>
        </authority>
    </funder>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_complete_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <name_swe>Ett namn</name_swe>
            <name_eng>Some name</name_eng>
            <end_date>2025-05-06</end_date>
            <identifier_organisationNumber>202100-5489</identifier_organisationNumber>
            <identifier_doi>10.1000/182</identifier_doi>
        </DATA_RECORD>       
        """
    )

    result = transform_funder(source_record)

    expected_xml = """
    <funder>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-funder</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <authority lang="swe" repeatId="swe">
            <name type="corporate">
                <namePart>Ett namn</namePart>
            </name>
        </authority>
        <authority lang="eng" repeatId="eng">
            <name type="corporate">
                <namePart>Some name</namePart>
            </name>
        </authority>
        <endDate>
            <year>2025</year>
            <month>05</month>
            <day>06</day>
        </endDate>
        <identifier type="doi">10.1000/182</identifier>
        <identifier type="organisationNumber">202100-5489</identifier>
    </funder>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_raises_error_when_source_record_has_unknown_element():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <some_unknown_element>Some unhandled value</some_unknown_element>
        </DATA_RECORD>       
        """
    )

    with pytest.raises(
        XMLValidationError,
        match="Unknown child element <some_unknown_element> found in <DATA_RECORD>",
    ):
        transform_funder(source_record)
