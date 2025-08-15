import xml.etree.ElementTree as ET
from db_to_cora.journal_transform import transform_journal
from common.test_helper import assert_equal_for_xml_and_xml_string

def test_required_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <title>some title</title>
            <subtitle>some subtitle</subtitle>
        </DATA_RECORD>       
        """
    )

    result = transform_journal(source_record)

    expected_xml = """
    <journal>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-journal</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <titleInfo>
            <title>some title</title>
            <subtitle> some subtitle</subtitle>
        </titleInfo>
    </journal>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    
def test_complete_xml():
    source_record = ET.fromstring(
        """
        <DATA_RECORD>
            <old_id>1234</old_id>
            <title>some title</title>
            <subtitle> some subtitle</subtitle>
            <end_date>2025-05-06</end_date>
            <url>url.se</url>
            <identifier_eissn>1234-1234</identifier_eissn>
            <identifier_pissn>5678-5678</identifier_pissn>
        </DATA_RECORD>
        """
    )

    result = transform_journal(source_record)
    secondResultSameRun = transform_journal(source_record)

    expected_xml = """
    <journal>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-journal</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>1234</oldId>
        </recordInfo>
        <titleInfo>
            <title>some title</title>
            <subtitle> some subtitle</subtitle>
        </titleInfo>
        <originInfo>
            <dateIssued point="end">
                <year>2025</year>
                <month>05</month>
                <day>06</day>
            </dateIssued>
        </originInfo>
        <identifier displayLabel="eissn" type="issn">1234-1234</identifier>
        <identifier displayLabel="pissn" type="issn">5678-5678</identifier>
        <location>
            <url>url.se</url>
        </location>
    </journal>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
    assert_equal_for_xml_and_xml_string(secondResultSameRun, expected_xml)
    
    
    
    