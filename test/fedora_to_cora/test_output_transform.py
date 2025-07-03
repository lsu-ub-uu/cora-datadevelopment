from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.output_transform import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml
from cora.context import MockContext


def test_output_transform(requests_mock):
    affiliation_organisation_id = "diva-organisation:15111790767789817"
    subject_id = "diva-subject:30224"

    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        text=_create_search_mock_response("organisation", affiliation_organisation_id),
    )
    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-subjectSearch",
        text=_create_search_mock_response("subject", subject_id),
    )

    fedora_xml = read_source_xml("test/data/fedora/mock_varldskulturmuserna.xml")

    result = transform_to_cora_output(
        fedora_xml,
        MockContext("https://pre.diva-portal.org/rest/record/", "test-token"),
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
        <subject lang="eng" repeatId="0">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
        <originInfo>
            <dateIssued>
                <year>2023</year>
            </dateIssued>
            <agent>
                <namePart repeatId="0">Uppsala Läroverk</namePart>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </agent>
            <place repeatId="0">
                <placeTerm>Stockholm</placeTerm>
            </place>
            <edition>3</edition>
        </originInfo>
        <extent>208</extent>
        <classification authority="ssif" repeatId="0">30224</classification>
        <classification authority="ssif" repeatId="1">60301</classification>
        <subject authority="diva">
            <topic repeatId="0">
                <linkedRecordType>diva-subject</linkedRecordType>
                <linkedRecordId>{subject_id}</linkedRecordId>
            </topic>
        </subject>
        <genre type="outputType">publication_edited-book</genre>
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <artisticWork type="outputType">false</artisticWork>
        <name repeatId="0" type="personal">
            <namePart type="family">Östasiatiska museet</namePart>
            <namePart type="given">Östasiatiska museet</namePart>
            <role>
                <roleTerm repeatId="0">edt</roleTerm>
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
        <adminInfo>
            <note type="internal">This is an internal note.</note>
            <reviewed>false</reviewed>
        </adminInfo>
        <identifier displayLabel="print" repeatId="0" type="isbn">978-91-506-2649-0</identifier>
        <identifier displayLabel="online" repeatId="1" type="isbn">978-92-893-7379-1</identifier>
        <identifier displayLabel="undefined" repeatId="2" type="isbn">978-92-893-7380-7</identifier>
        <identifier type="isrn">ISRN.01</identifier>
        <identifier type="archiveNumber">Arkivnummer.01</identifier>
        <identifier type="localId">LocalId.01</identifier>
        <identifier type="pmid">pmid123</identifier>
        <identifier type="wos">ISI.01</identifier>
        <identifier type="scopus">Scopus.01</identifier>
        <identifier type="patentNumber">Patentnummer01</identifier>
    </output>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def _create_search_mock_response(tag_name, record_id):
    return f"""
    <dataList>
        <data>
            <record>
                <data>
                    <{tag_name}>
                        <recordInfo>
                            <id>{record_id}</id>
                        </recordInfo>
                    </{tag_name}>
                </data>
            </record>
        </data>
    </dataList>
    """
