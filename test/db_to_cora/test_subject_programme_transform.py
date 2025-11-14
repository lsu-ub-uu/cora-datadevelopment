import xml.etree.ElementTree as ET

import pytest
from common.xml_validate import XMLValidationError
from db_to_cora.subject_programme_transform import transform_subject_programme
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_required_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <name_swe>En test</name_swe>
        </DATA_RECORD>      
        """
    )

    result = transform_subject_programme(source_record, "subject")

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_create_tag_for_programme():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <name_swe>En test</name_swe>
        </DATA_RECORD>      
        """
    )

    result = transform_subject_programme(source_record, "programme")

    expected_xml = """
        <programme>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-programme</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
        </programme>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_complete_without_links_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <end_date>2025-08-20</end_date>
            <name_swe>En test</name_swe>
            <name_eng>en testpost</name_eng>
        </DATA_RECORD>  
        """
    )

    result = transform_subject_programme(source_record, "subject")
    secondResultSameRun = transform_subject_programme(source_record, "subject")

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
            <variant lang="eng">
                <topic>en testpost</topic>
            </variant>
            <endDate>
                <year>2025</year>
                <month>08</month>
                <day>20</day>
            </endDate>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    assert_equal_for_xml_and_xml_string(secondResultSameRun, expected_xml)


def test_complete_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <end_date>2025-08-20</end_date>
            <name_swe>En test</name_swe>
            <name_eng>en testpost</name_eng>
            <broader_id>1234</broader_id>
            <earlier_id>9876</earlier_id>
        </DATA_RECORD>  
        """
    )

    result = transform_subject_programme(source_record, "subject")

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
            <authority lang="swe">
                <topic>En test</topic>
            </authority>
            <variant lang="eng">
                <topic>en testpost</topic>
            </variant>
            <endDate>
                <year>2025</year>
                <month>08</month>
                <day>20</day>
            </endDate>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_no_name_swe():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40102</old_id>
            <name_swe></name_swe>
        </DATA_RECORD>      
        """
    )

    result = transform_subject_programme(source_record, "subject")

    expected_xml = """
        <subject>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-subject</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>40102</oldId>
            </recordInfo>
        </subject>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_raises_error_when_unknown_element():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>40100</old_id>
            <end_date></end_date>
            <name_swe>Hotade kulturarv</name_swe>
            <name_eng>Hotade kulturarv</name_eng>
            <broader_id></broader_id>
            <parent_subject_id></parent_subject_id>
            <earlier_id></earlier_id>
            <some_unknown_element>some unknown value</some_unknown_element>
        </DATA_RECORD>       
        """
    )

    with pytest.raises(
        XMLValidationError,
        match="Unknown child element <some_unknown_element> found in <DATA_RECORD>",
    ):
        transform_subject_programme(source_record, "subject")
