import xml.etree.ElementTree as ET

import pytest
from common.xml_validate import XMLValidationError
from db_to_cora.series_transform import transform_series
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_required_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>1234</old_id>
            <title>Some title</title>
            <subtitle>Some subtitle</subtitle>
        </DATA_RECORD>       
        """
    )

    result = transform_series(source_record)

    expected_xml = """
        <series>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-series</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>1234</oldId>
            </recordInfo>
            <titleInfo>
                <title>Some title</title>
                <subtitle>Some subtitle</subtitle>
            </titleInfo>
        </series>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_complete_without_links_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>1234</old_id>
            <title>Some title</title>
            <subtitle>Some subtitle</subtitle>
            <alternative_title>Some alternative title</alternative_title>
            <alternative_subtitle>Some alternative subtitle</alternative_subtitle>
            <end_date>2025-08-05</end_date>
            <identifier_pissn>1234-1234</identifier_pissn>
            <identifier_eissn>9876-9876</identifier_eissn>
            <url>www.enurl.se</url>
            <external_note>Some note</external_note>
            <publication_type_id>59</publication_type_id>
        </DATA_RECORD>   
        """
    )

    result = transform_series(source_record)
    secondResultSameRun = transform_series(source_record)

    expected_xml = """
        <series>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-series</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>1234</oldId>
            </recordInfo>
            <titleInfo>
                <title>Some title</title>
                <subtitle>Some subtitle</subtitle>
            </titleInfo>
            <titleInfo type="alternative">
                <title>Some alternative title</title>
                <subtitle>Some alternative subtitle</subtitle>
            </titleInfo>
            <originInfo>
                <dateIssued point="end">
                    <year>2025</year>
                    <month>08</month>
                    <day>05</day>
                </dateIssued>
            </originInfo>
            <identifier displayLabel="pissn" type="issn">1234-1234</identifier>
            <identifier displayLabel="eissn" type="issn">9876-9876</identifier>
            <location>
                <url>www.enurl.se</url>
            </location>
            <note type="external">Some note</note>
            <genre repeatId="0" type="outputType">conference_paper</genre>
        </series>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    assert_equal_for_xml_and_xml_string(secondResultSameRun, expected_xml)


def skip_test_complete_xml_with_series_links():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>someDomain</domain>
            <old_id>1234</old_id>
            <title>Some title</title>
            <subtitle>Some subtitle</subtitle>
            <alternative_title>Some alternative title</alternative_title>
            <alternative_subtitle>Some alternative subtitle</alternative_subtitle>
            <end_date>2025-08-05</end_date>
            <identifier_pissn>1234-1234</identifier_pissn>
            <identifier_eissn>9876-9876</identifier_eissn>
            <url>www.enurl.se</url>
            <external_note>Some note</external_note>
            <publication_type_id>59</publication_type_id>
            <relative_id_host>diva-series:22116988688327947</relative_id_host>
            <relative_id_preceding>diva-series:22116988688327947</relative_id_preceding>
            <organisation_id>123</organisation_id>
        </DATA_RECORD>  
        """
    )

    result = transform_series(source_record)

    expected_xml = """
        <series>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-series</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>someDomain</linkedRecordId>
                </permissionUnit>
                <oldId>1234</oldId>
            </recordInfo>
            <titleInfo>
                <title>Some title</title>
                <subtitle>Some subtitle</subtitle>
            </titleInfo>
            <titleInfo type="alternative">
                <title>Some alternative title</title>
                <subtitle>Some alternative subtitle</subtitle>
            </titleInfo>
            <originInfo>
                <dateIssued point="end">
                    <year>2025</year>
                    <month>08</month>
                    <day>05</day>
                </dateIssued>
            </originInfo>
            <identifier displayLabel="pissn" type="issn">1234-1234</identifier>
            <identifier displayLabel="eissn" type="issn">9876-9876</identifier>
            <location>
                <url>www.enurl.se</url>
            </location>
            <note type="external">Some note</note>
            <genre repeatId="0" type="outputType">conference_paper</genre>
            <organisation>
                <linkedRecordType>diva-organisation</linkedRecordType>
                <linkedRecordId>123</linkedRecordId>
            </organisation>
            <related repeatId="1" type="host">
                <series>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:22116988688327947</linkedRecordId>
                </series>
            </related>
            <related repeatId="2" type="preceding">
                <series>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:22116988688327947</linkedRecordId>
                </series>
            </related>
        </series>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_no_title():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>varldskulturmuseerna</domain>
            <old_id>1234</old_id>
            <title></title>
            <subtitle></subtitle>
        </DATA_RECORD>       
        """
    )

    result = transform_series(source_record)

    expected_xml = """
        <series>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-series</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>varldskulturmuseerna</linkedRecordId>
                </permissionUnit>
                <oldId>1234</oldId>
            </recordInfo>
        </series>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_raises_error_when_unknown_element():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <domain>someDomain</domain>
            <old_id>1234</old_id>
            <title>Some title</title>
            <subtitle>Some subtitle</subtitle>
            <alternative_title>Some alternative title</alternative_title>
            <alternative_subtitle>Some alternative subtitle</alternative_subtitle>
            <end_date>2025-08-05</end_date>
            <identifier_pissn>1234-1234</identifier_pissn>
            <identifier_eissn>9876-9876</identifier_eissn>
            <url>www.enurl.se</url>
            <external_note>Some note</external_note>
            <publication_type_id>59</publication_type_id>
            <relative_id_host>diva-series:22116988688327947</relative_id_host>
            <relative_id_preceding>diva-series:22116988688327947</relative_id_preceding>
            <organisation_id>123</organisation_id>
            <some_unknown_element>some unknown value</some_unknown_element>
        </DATA_RECORD>       
        """
    )

    with pytest.raises(
        XMLValidationError,
        match="Unknown child element <some_unknown_element> found in <DATA_RECORD>",
    ):
        transform_series(source_record)
