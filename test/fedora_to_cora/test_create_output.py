from common.test_helper import assert_equal_for_xml_and_xml_string, MockCoraConfig
from fedora_to_cora.create_output import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml


def test_creates_output(requests_mock):
    affiliation_organisation_id = "diva-organisation:15111790767789817"
    mock_response = f"""
    <dataList>
        <data>
            <record>
                <data>
                    <organisation>
                        <recordInfo>
                            <id>{affiliation_organisation_id}</id>
                        </recordInfo>
                    </organisation>
                </data>
            </record>
        </data>
    </dataList>
    """

    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        text=mock_response,
    )

    fedora_xml = read_source_xml("test/data/fedora/mock_varldskulturmuserna.xml")

    result = transform_to_cora_output(
        fedora_xml,
        MockCoraConfig("https://pre.diva-portal.org/rest/record/", "test-token"),
    )

    expected_xml = f"""
    <output>
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>publication_edited-book</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <permissionUnit>
                <linkedRecordType>permissionUnit</linkedRecordType>
                <linkedRecordId>varldskulturmuseerna</linkedRecordId>
            </permissionUnit>
            <visibility>published</visibility>
            <oldId>diva2:1681782</oldId>
        </recordInfo>
        <genre type="contentType">ref</genre>
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
        </titleInfo>
        <subject lang="eng">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
        <originInfo>
            <dateIssued>
                <year>2023</year>
            </dateIssued>
        </originInfo>
        <genre type="outputType">publication_edited-book</genre>
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <artisticWork type="outputType">false</artisticWork>
        <name repeatId="0" type="personal">
            <namePart type="family">Östasiatiska museet</namePart>
            <namePart type="given">Östasiatiska museet</namePart>
            <role>
                <roleTerm repeatId="0" type="code">edt</roleTerm>
            </role>
            <affiliation repeatId="0">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>{affiliation_organisation_id}</linkedRecordId>
                </organisation>
            </affiliation>
        </name>
        <note type="creatorCount">1</note>
        <abstract lang="swe" repeatId="0">
            Lorem ipsum dolor sit amet
        </abstract>
        <admin>
            <note type="internal">This is an internal note.</note>
            <reviewed>false</reviewed>
        </admin>
        <identifier displayLabel="print" repeatId="0" type="isbn">978-91-506-2649-0</identifier>
        <identifier displayLabel="online" repeatId="1" type="isbn">978-92-893-7379-1</identifier>
        <identifier displayLabel="invalid" repeatId="2" type="isbn">978-92-893-7380-7</identifier>
        <identifier type="isrn">ISRN.01</identifier>
    </output>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
