from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.output_transform import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml
from cora.context import MockContext


def test_output_transform(requests_mock):
    affiliation_organisation_id = "diva-organisation:15111790767789817"
    subject_id = "diva-subject:30224"
    series_id = "diva-series:17450"

    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch",
        text=_create_search_mock_response("organisation", affiliation_organisation_id),
    )
    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-subjectSearch",
        text=_create_search_mock_response("subject", subject_id),
    )
    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-seriesSearch",
        text=_create_search_mock_response("series", series_id),
    )

    fedora_xml = read_source_xml("test/data/fedora/mock_publication_ultimate.xml")

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
        <dataQuality>2026</dataQuality>
        <genre type="contentType">ref</genre>
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
        </titleInfo>
        <subject lang="eng" repeatId="0">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
        <dateOther type="patent">
            <year>2022</year>
            <month>08</month>
            <day>15</day>
        </dateOther>
        <originInfo>
            <dateIssued>
                <year>2023</year>
            </dateIssued>
            <agent repeatId="0">
                <namePart>Uppsala Läroverk</namePart>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </agent>
            <place repeatId="0">
                <placeTerm>Stockholm</placeTerm>
            </place>
            <edition>3</edition>
        </originInfo>
        <physicalDescription>
            <extent>208</extent>
        </physicalDescription>
        <classification authority="ssif" repeatId="0">30224</classification>
        <classification authority="ssif" repeatId="1">60301</classification>
        <subject authority="diva">
            <topic repeatId="0">
                <linkedRecordType>diva-subject</linkedRecordType>
                <linkedRecordId>{subject_id}</linkedRecordId>
            </topic>
        </subject>
        <genre type="outputType">publication_edited-book</genre>
        <genre type="subcategory">policyDocument</genre>
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <note type="publicationStatus">published</note>
        <artisticWork type="outputType">false</artisticWork>
        <name type="personal" repeatId="0">
            <namePart type="family">Andersson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <nameIdentifier type="localId">mican434</nameIdentifier>
            <nameIdentifier type="orcid">0000-0002-3134-8865</nameIdentifier>
        </name>
        <name type="personal" repeatId="1">
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
        <typeOfResource>stillImage</typeOfResource>
        <type lang="swe" repeatId="0">
            Typ01
        </type>
        <type lang="swe" repeatId="1">
            Typ02
        </type>
        <material lang="swe" repeatId="0">
            Material01
        </material>
        <material lang="swe" repeatId="1">
            Material02
        </material>
        <technique lang="swe" repeatId="0">
            Teknik01
        </technique>
        <technique lang="swe" repeatId="1">
            Teknik02
        </technique>
        <size>
            22*32 km2
        </size>
        <duration>
            <hh>01</hh>
            <mm>10</mm>
            <ss>00</ss>
        </duration>
        <abstract lang="swe" repeatId="0">
            Lorem ipsum dolor sit amet
        </abstract>
        <adminInfo>
            <note type="internal">This is an internal note.</note>
            <reviewed>false</reviewed>
        </adminInfo>
        <subject authority="sdg">
            <topic repeatId="0">sdg1</topic>
        </subject>
        <identifier displayLabel="print" repeatId="0" type="isbn">978-91-506-2649-0</identifier>
        <identifier displayLabel="online" repeatId="1" type="isbn">978-92-893-7379-1</identifier>
        <identifier displayLabel="undefined" repeatId="2" type="isbn">978-92-893-7380-7</identifier>
        <identifier type="isrn">ISRN.01</identifier>
        <identifier type="archiveNumber">Arkivnummer.01</identifier>
        <identifier type="localId" repeatId="0">LocalId.01</identifier>
        <identifier type="pmid">pmid123</identifier>
        <identifier type="wos">ISI.01</identifier>
        <identifier type="scopus">Scopus.01</identifier>
        <identifier type="se-libr">0004</identifier>
        <identifier type="doi">10.1038/s41698-022-00278-4</identifier>
        <identifier type="patentNumber">Patentnummer01</identifier>
        <location repeatId="0">
            <url>http://example.com</url>
            <displayLabel>BMFEA vol 1-75</displayLabel>
        </location>
        <note type="external">This is an external note.</note>
        <relatedItem type="series" otherType="link" repeatId="controlled0">
            <series>
                <linkedRecordType>diva-series</linkedRecordType>
                <linkedRecordId>{series_id}</linkedRecordId>
            </series>
            <partNumber>1-75</partNumber>
        </relatedItem>
        <relatedItem type="conference">
            <conference>Some conference</conference>
        </relatedItem>
        <studentDegree repeatId="0">
            <degreeLevel>H2</degreeLevel>
            <universityPoints>20</universityPoints>
        </studentDegree>...
        <externalCollaboration>
            <namePart repeatId="0">En extern partner</namePart>
            <namePart repeatId="1">Ytterligare extern partner</namePart>
        </externalCollaboration>
        <degreeGrantingInstitution type="corporate" otherType="text">
            <namePart>Uppsala universitet</namePart>
            <role>
                <roleTerm>dgg</roleTerm>
            </role>
        </degreeGrantingInstitution>
        <supervisor type="personal" repeatId="0">
            <namePart type="family">Handledare</namePart>
            <namePart type="given">Helge</namePart>
            <role>
                <roleTerm repeatId="0">ths</roleTerm>
            </role>
        </supervisor>
        <examiner type="personal" repeatId="0">
            <namePart type="family">Examinator</namePart>
            <namePart type="given">Erik</namePart>
            <role>
                <roleTerm repeatId="0">dgs</roleTerm>
            </role>
        </examiner>
        <opponent type="personal" repeatId="0">
            <namePart type="family">Opponent</namePart>
            <namePart type="given">Olivia</namePart>
            <role>
                <roleTerm repeatId="0">opn</roleTerm>
            </role>
        </opponent>
        <academicSemester>
            <year>2022</year>
            <academicSemester>ht</academicSemester>
        </academicSemester>
        <externalCollaboration>
            <namePart repeatId="0">
                En extern partner
            </namePart>
            <namePart repeatId="1">
                Ytterligare extern partner
            </namePart>
        </externalCollaboration>
        <studentDegree repeatId="0">
            <degreeLevel>H2</degreeLevel>
            <universityPoints>20</universityPoints>
        </studentDegree>
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
            <address>Slottet</address>
            <place>
                <placeTerm>
                    Uppsala
                </placeTerm>
            </place>
        </defence>
        <relatedItem type="journal" otherType="text">
            <titleInfo>
                <title>Design, Automation and Test in Europe</title>
            </titleInfo>
            <identifier type="issn" displayLabel="pissn">
                1530-1591
            </identifier>
            <identifier type="issn" displayLabel="eissn">
                1558-1101
            </identifier>
        </relatedItem>
        <relatedItem type="project" otherType="text" repeatId="uncontrolled0">
            <titleInfo>
                <title>Ett annat projekt</title>
            </titleInfo>
        </relatedItem>
        <relatedItem type="project" otherType="text" repeatId="uncontrolled1">
            <titleInfo>
                <title>Ytterligare ett annat projekt</title>
            </titleInfo>
        </relatedItem>

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
