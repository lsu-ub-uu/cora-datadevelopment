from common.test_helper import assert_equal_for_xml_and_xml_string
from common.xml_utils import pretty_print_xml
from fedora_to_cora.output_transform import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml
from cora.context import MockContext
import pytest


@pytest.fixture
def mock_diva_search_requests(requests_mock):
    """
    Fixture to mock DIVA search requests and return IDs for testing.

    Returns:
        dict: A dictionary containing the IDs used in the mocked responses:
            - affiliation_organisation_id: str
            - subject_id: str
            - series_id: str
            - publisher_id: str
    """
    affiliation_organisation_id = "diva-organisation:15111790767789817"
    subject_id = "diva-subject:30224"
    series_id = "diva-series:17450"
    publisher_id = "diva-publisher:12345"
    funder_id = "diva-funder:67890"

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
    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-publisherSearch",
        text=_create_search_mock_response("publisher", publisher_id),
    )
    requests_mock.get(
        "https://pre.diva-portal.org/rest/record/searchResult/diva-funderSearch",
        text=_create_search_mock_response("funder", funder_id),
    )

    return {
        "affiliation_organisation_id": affiliation_organisation_id,
        "subject_id": subject_id,
        "series_id": series_id,
        "publisher_id": publisher_id,
        "funder_id": funder_id,
    }


def test_output_transform_ultimate(mock_diva_search_requests):
    ids = mock_diva_search_requests
    affiliation_organisation_id = ids["affiliation_organisation_id"]
    subject_id = ids["subject_id"]
    series_id = ids["series_id"]

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
                <linkedRecordId>publication_other</linkedRecordId>
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
            <urn>urn:nbn:se:varldskulturmuseerna:diva-6</urn>
        </recordInfo>
        <dataQuality>2026</dataQuality>
        <genre type="outputType">publication_other</genre>
        <genre type="subcategory">policyDocument</genre>
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <note type="publicationStatus">published</note>
        <artisticWork type="outputType">false</artisticWork>
        <genre type="contentType">ref</genre>
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
        </titleInfo>
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
        <name type="corporate" repeatId="0">
            <organisation>
                <linkedRecordType>diva-organisation</linkedRecordType>
                <linkedRecordId>{affiliation_organisation_id}</linkedRecordId>
            </organisation>
            <role><roleTerm repeatId="0">cre</roleTerm></role>
        </name>
        <note type="creatorCount">1</note>
        <typeOfResource>stillImage</typeOfResource>
        <type lang="swe" repeatId="0">Typ01</type>
        <type lang="swe" repeatId="1">Typ02</type>
        <material lang="swe" repeatId="0">Material01</material>
        <material lang="swe" repeatId="1">Material02</material>
        <technique lang="swe" repeatId="0">Teknik01</technique>
        <technique lang="swe" repeatId="1">Teknik02</technique>
        <size>22*32 km2</size>
        <duration><hh>01</hh><mm>10</mm><ss>00</ss></duration>
        <physicalDescription><extent unit="pages">208</extent></physicalDescription>
        <note type="context" lang="swe" repeatId="0">Fritextbeskrivning Fritextbeskrivning</note>
        <abstract lang="swe" repeatId="0">Lorem ipsum dolor sit amet</abstract>
        <subject lang="eng" repeatId="0"><topic>Sinology</topic></subject>
        <subject lang="eng" repeatId="1"><topic>Archeology</topic></subject>
        <subject lang="swe" repeatId="2"><topic>Sinologi</topic></subject>
        <subject lang="swe" repeatId="3"><topic>Arkeologi</topic></subject>
        <dateOther type="patent"><year>2022</year><month>08</month><day>15</day></dateOther>
        <name type="corporate" otherType="patentHolder"><namePart>Patentorganisation</namePart><role><roleTerm>pth</roleTerm></role></name>
        <patentCountry>au</patentCountry>
        <originInfo><dateIssued><year>2023</year></dateIssued><agent repeatId="0"><namePart>Uppsala Läroverk</namePart><role><roleTerm>pbl</roleTerm></role></agent><place repeatId="0"><placeTerm>Stockholm</placeTerm></place><edition>3</edition></originInfo>
        <classification authority="ssif" repeatId="0">30224</classification>
        <classification authority="ssif" repeatId="1">60301</classification>
        <subject authority="sdg"><topic repeatId="0">sdg1</topic></subject>
        <subject authority="diva"><topic repeatId="0"><linkedRecordType>diva-subject</linkedRecordType><linkedRecordId>{subject_id}</linkedRecordId></topic></subject>
        <identifier displayLabel="print" repeatId="0" type="isbn">978-91-506-2649-0</identifier>
        <identifier displayLabel="online" repeatId="1" type="isbn">978-92-893-7379-1</identifier>
        <identifier displayLabel="undefined" repeatId="2" type="isbn">978-92-893-7380-7</identifier>
        <identifier type="isrn">ISRN.01</identifier>
        <identifier type="patentNumber">Patentnummer01</identifier>
        <identifier type="doi">10.1038/s41698-022-00278-4</identifier>
        <identifier type="pmid">pmid123</identifier>
        <identifier type="wos">ISI.01</identifier>
        <identifier type="scopus">Scopus.01</identifier>
        <identifier type="se-libr" repeatId="0">0004</identifier>
        <identifier type="se-libr" repeatId="1">0005</identifier>
        <identifier type="archiveNumber">Arkivnummer.01</identifier>
        <identifier type="localId" repeatId="0">LocalId.01</identifier>
        <location repeatId="0"><url>http://example.com</url><displayLabel>BMFEA vol 1-75</displayLabel></location>
        <location displayLabel="orderLink"><url>http://acta.mamutweb.com/Shop/Product/0476-Laparoscopic-or-Open-Inguinal-Hernia-Repair---Whic/diva2:232194</url><displayLabel>Beställ/Order</displayLabel></location>
        <note type="external">This is an external note.</note>
        <academicSemester><year>2022</year><academicSemester>ht</academicSemester></academicSemester>
        <studentDegree repeatId="0"><degreeLevel>H2</degreeLevel><universityPoints>20</universityPoints></studentDegree>
        <externalCollaboration><namePart repeatId="0">En extern partner</namePart><namePart repeatId="1">Ytterligare extern partner</namePart></externalCollaboration>
        <name type="corporate" otherType="degreeGrantingInstitution"><namePart>Uppsala universitet</namePart><role><roleTerm>dgg</roleTerm></role></name>
        <name type="personal" otherType="thesisAdvisor" repeatId="0"><namePart type="family">Handledare</namePart><namePart type="given">Helge</namePart><role><roleTerm repeatId="0">ths</roleTerm></role></name>
        <name type="personal" otherType="degreeSupervisor" repeatId="0"><namePart type="family">Examinator</namePart><namePart type="given">Erik</namePart><role><roleTerm repeatId="0">dgs</roleTerm></role></name>
        <name type="personal" otherType="opponent" repeatId="0"><namePart type="family">Opponent</namePart><namePart type="given">Olivia</namePart><role><roleTerm repeatId="0">opn</roleTerm></role></name>
        <defence><language><languageTerm type="code" authority="iso639-2b">swe</languageTerm></language><dateOther type="presentation"><year>2022</year><month>07</month><day>31</day><hh>16</hh><mm>19</mm></dateOther><address><location>Balsalen</location><street>Slottet</street><city>Uppsala</city></address></defence>
        <relatedItem type="journal" otherType="text"><titleInfo><title>Design, Automation and Test in Europe</title></titleInfo><identifier type="issn" displayLabel="pissn">1530-1591</identifier><identifier type="issn" displayLabel="eissn">1558-1101</identifier><part><detail type="volume"><number>15</number></detail><detail type="issue"><number>4</number></detail><detail type="artNo"><number>ART-2022-04</number></detail><extent><start>10</start><end>30</end></extent></part></relatedItem>
        <relatedItem type="conference"><conference>Some conference</conference></relatedItem>
        <relatedItem type="publicationChannel"><publicationChannel>Discovery Channel</publicationChannel></relatedItem>
        <relatedItem type="series" otherType="link" repeatId="controlled0"><series><linkedRecordType>diva-series</linkedRecordType><linkedRecordId>{series_id}</linkedRecordId></series><partNumber>1-75</partNumber></relatedItem>
        <relatedItem type="project" otherType="text" repeatId="uncontrolled0"><titleInfo><title>Ett annat projekt</title></titleInfo></relatedItem>
        <relatedItem type="project" otherType="text" repeatId="uncontrolled1"><titleInfo><title>Ytterligare ett annat projekt</title></titleInfo></relatedItem>
        <relatedItem type="project" otherType="text" repeatId="funderProjectId0"><identifier type="project">2021-00001</identifier></relatedItem>
        <relatedItem type="project" otherType="text" repeatId="funderProjectId1"><identifier type="project">2021-00002</identifier></relatedItem>
        <name repeatId="0" type="corporate" otherType="funder">
            <funder>
                <linkedRecordType>diva-funder</linkedRecordType>
                <linkedRecordId>diva-funder:67890</linkedRecordId>
            </funder>
            <role><roleTerm>fnd</roleTerm></role>
        </name>
        <name repeatId="1" type="corporate" otherType="funder">
            <funder>
                <linkedRecordType>diva-funder</linkedRecordType>
                <linkedRecordId>diva-funder:67890</linkedRecordId>
            </funder>
            <role><roleTerm>fnd</roleTerm></role>
        </name>
        <adminInfo><note type="internal">This is an internal note.</note><reviewed>false</reviewed></adminInfo>
    </output>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)


def test_output_transform_book(mock_diva_search_requests):
    ids = mock_diva_search_requests
    publisher_id = ids["publisher_id"]
    subject_id = ids["subject_id"]

    source_xml = read_source_xml("test/data/fedora/mock_publication_book.xml")
    result = transform_to_cora_output(source_xml, MockContext())

    assert_equal_for_xml_and_xml_string(
        result,
        f"""
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_book</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>nordiskamuseet</linkedRecordId>
                </permissionUnit>
                <visibility>published</visibility>
                <oldId>diva2:1179703</oldId>
                <urn>urn:nbn:se:nordiskamuseet:diva-39</urn>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">publication_book</genre>
            <language repeatId="0">
                <languageTerm type="code" authority="iso639-2b">swe</languageTerm>
            </language>
            <artisticWork type="outputType">false</artisticWork>
            <genre type="contentType">vet</genre>
            <titleInfo lang="swe">
                <title>Känn dig själv</title>
                <subtitle>Nordiska museets och Skansens årsbok Fataburen 1998</subtitle>
            </titleInfo>
            <name type="personal" repeatId="0">
                <namePart type="family">Bergman</namePart>
                <namePart type="given">Ingrid</namePart>
                <namePart type="date">1934-2013</namePart>
                <role>
                    <roleTerm repeatId="0">edt</roleTerm>
                </role>
                <affiliation repeatId="0">
                    <organisation>
                        <linkedRecordType>diva-organisation</linkedRecordType>
                        <linkedRecordId>diva-organisation:15111790767789817</linkedRecordId>
                    </organisation>
                </affiliation>
            </name>
            <physicalDescription>
                <extent unit="pages">335</extent>
            </physicalDescription>
            <subject lang="swe" repeatId="0">
                <topic>Kulturarv</topic>
            </subject>
            <subject lang="swe" repeatId="1">
                <topic>Skansen</topic>
            </subject>
            <originInfo>
                <dateIssued>
                    <year>1997</year>
                </dateIssued>
                <agent repeatId="0">
                    <publisher>
                        <linkedRecordType>diva-publisher</linkedRecordType>
                        <linkedRecordId>{publisher_id}</linkedRecordId>
                    </publisher>
                    <role>
                        <roleTerm>pbl</roleTerm>
                    </role>
                </agent>
                <place repeatId="0">
                    <placeTerm>Stockholm</placeTerm>
                </place>
            </originInfo>
            <classification authority="ssif" repeatId="0">60503</classification>
            <subject authority="diva">
                <topic repeatId="0">
                    <linkedRecordType>diva-subject</linkedRecordType>
                    <linkedRecordId>{subject_id}</linkedRecordId>
                </topic>
            </subject>
            <identifier type="isbn" displayLabel="print" repeatId="0">9171084282</identifier>
            <identifier type="localId" repeatId="0">xxxxx</identifier>
            <relatedItem type="series" otherType="link" repeatId="controlled0">
                <series>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:17450</linkedRecordId>
                </series>
                <partNumber>1998</partNumber>
            </relatedItem>
            <adminInfo>
                <reviewed>true</reviewed>
            </adminInfo>
        </output>                   
    """,
    )


def test_output_transform_book_chapter(mock_diva_search_requests):
    ids = mock_diva_search_requests
    publisher_id = ids["publisher_id"]
    subject_id = ids["subject_id"]

    source_xml = read_source_xml("test/data/fedora/mock_publication_book-chapter.xml")
    result = transform_to_cora_output(source_xml, MockContext())

    assert_equal_for_xml_and_xml_string(
        result,
        f"""
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_book-chapter</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>nordiskamuseet</linkedRecordId>
                </permissionUnit>
                <visibility>published</visibility>
                <oldId>diva2:1365846</oldId>
                <urn>urn:nbn:se:nordiskamuseet:diva-2126</urn>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">publication_book-chapter</genre>
            <language repeatId="0">
                <languageTerm type="code" authority="iso639-2b">swe</languageTerm>
            </language>
            <artisticWork type="outputType">false</artisticWork>
            <genre type="contentType">vet</genre>
            <titleInfo lang="swe">
                <title>När två var ett</title>
                <subtitle>Skansen och Nordiska museet</subtitle>
            </titleInfo>
            <name type="personal" repeatId="0">
                <namePart type="family">Mockson</namePart>
                <namePart type="given">Mock</namePart>
                <namePart type="date">1954</namePart>
                <role>
                    <roleTerm repeatId="0">aut</roleTerm>
                </role>
                <affiliation repeatId="0">
                    <organisation>
                        <linkedRecordType>diva-organisation</linkedRecordType>
                        <linkedRecordId>diva-organisation:15111790767789817</linkedRecordId>
                    </organisation>
                </affiliation>
            </name>
            <subject lang="swe" repeatId="0">
                <topic>Skansen</topic>
            </subject>
            <subject lang="swe" repeatId="1">
                <topic>Nordiska museet</topic>
            </subject>
            <originInfo>
                <dateIssued>
                    <year>2016</year>
                </dateIssued>
                <agent repeatId="0">
                    <publisher>
                        <linkedRecordType>diva-publisher</linkedRecordType>
                        <linkedRecordId>{publisher_id}</linkedRecordId>
                    </publisher>
                    <role>
                        <roleTerm>pbl</roleTerm>
                    </role>
                </agent>
                <place repeatId="0">
                    <placeTerm>Stockholm</placeTerm>
                </place>
            </originInfo>
            <classification authority="ssif" repeatId="0">605</classification>
            <subject authority="diva">
                <topic repeatId="0">
                    <linkedRecordType>diva-subject</linkedRecordType>
                    <linkedRecordId>{subject_id}</linkedRecordId>
                </topic>
                <topic repeatId="1">
                    <linkedRecordType>diva-subject</linkedRecordType>
                    <linkedRecordId>{subject_id}</linkedRecordId>
                </topic>
            </subject>

            <identifier type="localId" repeatId="0">xxxxx</identifier>
            <relatedItem type="book" otherType="text">
                <titleInfo>
                    <title>Skansen 125</title>
                </titleInfo>
                <note type="statementOfResponsibility">Fejkelina Jönsson</note>
                <identifier displayLabel="print" repeatId="0" type="isbn">978-91-506-2649-0</identifier>
                <identifier displayLabel="online" repeatId="1" type="isbn">978-92-893-7379-1</identifier>
                <identifier displayLabel="undefined" repeatId="2" type="isbn">978-92-893-7380-7</identifier>
                <identifier type="doi">10.1038/s41698-022-00278-4</identifier>
                <identifier type="se-libr" repeatId="0">0004</identifier>
                <identifier type="se-libr" repeatId="1">0005</identifier>
                <part>
                    <extent>
                        <start>122</start>
                        <end>143</end>
                    </extent>
                </part>
                <relatedItem type="series" otherType="link" repeatId="controlled0">
                    <series>
                        <linkedRecordType>diva-series</linkedRecordType>
                        <linkedRecordId>diva-series:17450</linkedRecordId>
                    </series>
                    <partNumber>2016</partNumber>
                </relatedItem>
            </relatedItem>
            <adminInfo>
                <reviewed>false</reviewed>
            </adminInfo>
        </output>                   
    """,
    )


def test_output_transform_student_thesis(mock_diva_search_requests):
    fedora_xml = read_source_xml("test/data/fedora/mock_publication_student-thesis.xml")

    result = transform_to_cora_output(fedora_xml, MockContext())

    assert_equal_for_xml_and_xml_string(
        result,
        f"""
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva_degree-project</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>nordiskamuseet</linkedRecordId>
                </permissionUnit>
                <visibility>published</visibility>
                <oldId>diva2:1297418</oldId>
                <urn>urn:nbn:se:nordiskamuseet:diva-1431</urn>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">diva_degree-project</genre>
            <language repeatId="0">
                <languageTerm authority="iso639-2b" type="code">swe</languageTerm>
            </language>
            <artisticWork type="outputType">false</artisticWork>
            <titleInfo lang="swe">
                <title>Nationellt och smakfullt</title>
                <subtitle>omvärderingen av den gustavianska stilen och lanseringen av Georg Haupt som estetiskt ideal</subtitle>
            </titleInfo>
            <name repeatId="0" type="personal">
                <namePart type="family">Studentson</namePart>
                <namePart type="given">Mock</namePart>
                <namePart type="date">1965</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
                <affiliation repeatId="0">
                    <organisation>
                        <linkedRecordType>diva-organisation</linkedRecordType>
                        <linkedRecordId>{mock_diva_search_requests["affiliation_organisation_id"]}</linkedRecordId>
                    </organisation>
                </affiliation>
            </name>
            <physicalDescription>
                <extent unit="pages">64</extent>
            </physicalDescription>
            <subject lang="swe" repeatId="0">
                <topic>Möbelkonst</topic>
            </subject>
            <subject lang="swe" repeatId="1">
                <topic>Gustaviansk stil</topic>
            </subject>
            <subject lang="swe" repeatId="2">
                <topic>Nationell identitet</topic>
            </subject>
            <originInfo>
                <dateIssued>
                    <year>2012</year>
                </dateIssued>
            </originInfo>
            <classification authority="ssif" repeatId="0">60407</classification>
            <academicSemester>
                <year>2012</year>
                <academicSemester>vt</academicSemester>
            </academicSemester>
            <studentDegree repeatId="0">
                <degreeLevel>H1</degreeLevel>
                <universityPoints>180</universityPoints>
            </studentDegree>
            <externalCollaboration>
                <namePart repeatId="0">Stockholms Universitet, Konstvetenskapliga institutionen</namePart>
            </externalCollaboration>
            <name type="personal" otherType="thesisAdvisor" repeatId="0">
            <namePart type="family">Handledare</namePart>
            <namePart type="given">Helge</namePart>
                <role>
                    <roleTerm repeatId="0">ths</roleTerm>
                </role>
            </name>
            <name type="personal" otherType="degreeSupervisor" repeatId="0">
                <namePart type="family">Examinator</namePart>
                <namePart type="given">Erik</namePart>
                <role>
                    <roleTerm repeatId="0">dgs</roleTerm>
                </role>
            </name>
            <adminInfo>
                <reviewed>true</reviewed>
            </adminInfo>
        </output>                     
    """,
    )


def test_output_transform_conference_paper(mock_diva_search_requests):
    fedora_xml = read_source_xml(
        "test/data/fedora/mock_publication_conference-paper.xml"
    )

    result = transform_to_cora_output(fedora_xml, MockContext())

    assert_equal_for_xml_and_xml_string(
        result,
        f"""
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>conference_paper</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>uu</linkedRecordId>
                </permissionUnit>
                <visibility>published</visibility>
                <oldId>diva2:807059</oldId>
                <urn>urn:nbn:se:uu:diva-249061</urn>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">conference_paper</genre>
            <language repeatId="0">
                <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
            </language>
            <artisticWork type="outputType">false</artisticWork>
            <genre type="contentType">ref</genre>
            <titleInfo lang="eng">
                <title>Laser heated ferromagnetic simulations</title>
            </titleInfo>
            <name repeatId="0" type="personal">
                <namePart type="family">Mocksson</namePart>
                <namePart type="given">Mock</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
                <nameIdentifier type="localId">XXXXX</nameIdentifier>
            </name>
            <name repeatId="1" type="personal">
                <namePart type="family">Mockson</namePart>
                <namePart type="given">Mock</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
                <nameIdentifier type="localId">XXXXX</nameIdentifier>
            </name>
            <name repeatId="2" type="personal">
                <namePart type="family">Mockson</namePart>
                <namePart type="given">Mock</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
                <nameIdentifier type="localId">XXXXX</nameIdentifier>
            </name>
            <name repeatId="3" type="personal">
                <namePart type="family">Mockson</namePart>
                <namePart type="given">Mock</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
            </name>
            <name repeatId="4" type="personal">
                <namePart type="family">Mockson</namePart>
                <namePart type="given">Mock</namePart>
                <role>
                    <roleTerm>aut</roleTerm>
                </role>
            </name>
            <abstract lang="eng" repeatId="0">Hej</abstract>
            <originInfo>
                <dateIssued>
                    <year>2015</year>
                </dateIssued>
            </originInfo>
            <classification authority="ssif" repeatId="0">10399</classification>
            <identifier type="wos">000349745400025</identifier>
            <relatedItem otherType="text" type="proceeding">
                <titleInfo>
                    <title>Ultrafast Magnetism I</title>
                </titleInfo>
                <note type="statementOfResponsibility">Doe, John</note>
                <part>
                    <extent>
                    <start>76</start>
                    <end>78</end>
                    </extent>
                </part>
                <identifier displayLabel="print" repeatId="0" type="isbn">978-3-319-07743-7; 978-3-319-07742-0</identifier>
                <identifier type="doi">10.1007/978-3-319-07743-7_25</identifier>
                <relatedItem otherType="text" repeatId="uncontrolled0" type="series">
                    <titleInfo>
                        <title>Springer Proceedings in Physics</title>
                    </titleInfo>
                    <identifier displayLabel="pissn" type="issn">0930-8989</identifier>
                    <partNumber>159</partNumber>
                </relatedItem>
            </relatedItem>
            <relatedItem type="conference">
                <conference>Ultrafast Magnetization Conference, OCT 28-NOV 01, 2013, Strasbourg, FRANCE</conference>
            </relatedItem>
            <adminInfo>
                <reviewed>true</reviewed>
            </adminInfo>
        </output>                     
    """,
    )


def test_output_transform_minimal():
    fedora_xml = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>50</publicationTypeId>
                <publicationTypeCode>article</publicationTypeCode>
            </publicationType>
            <pid>diva2:1111</pid>
            <administrativeInfo>
                <domain>kth</domain>
            </administrativeInfo>
        </publication>
        """
    )

    result = transform_to_cora_output(
        fedora_xml,
        MockContext(),
    )

    assert_equal_for_xml_and_xml_string(
        result,
        """
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_journal-article</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>kth</linkedRecordId>
                </permissionUnit>
                <visibility>unpublished</visibility>
                <oldId>diva2:1111</oldId>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">publication_journal-article</genre>
        </output>                      
    """,
    )


def test_output_transform_with_missing_data():
    fedora_xml = ET.fromstring(
        """
        <publication>
            <contentType>
                <contentTypeId>50</contentTypeId>
                <contentTypeCode>refereed</contentTypeCode>
                <contentTypeNames>
                    <contentTypeName>
                        <contentTypeNameId>106</contentTypeNameId>
                        <locale>no</locale>
                        <contentTypeName>Fagfellevurdert</contentTypeName>
                    </contentTypeName>
                    <contentTypeName>
                        <contentTypeNameId>101</contentTypeNameId>
                        <locale>sv</locale>
                        <contentTypeName>Refereegranskat</contentTypeName>
                    </contentTypeName>
                    <contentTypeName>
                        <contentTypeNameId>100</contentTypeNameId>
                        <locale>en</locale>
                        <contentTypeName>Refereed</contentTypeName>
                    </contentTypeName>
                </contentTypeNames>
            </contentType>
            <publicationType>
                <publicationTypeId>58</publicationTypeId>
                <publicationTypeCode>chapter</publicationTypeCode>
                <openUrlType>bookitem</openUrlType>
                <publicationTypeNames>
                    <publicationTypeName>
                        <publicationTypeNameId>217</publicationTypeNameId>
                        <locale>en</locale>
                        <publicationTypeName>Chapter in book</publicationTypeName>
                    </publicationTypeName>
                    <publicationTypeName>
                        <publicationTypeNameId>216</publicationTypeNameId>
                        <locale>sv</locale>
                        <publicationTypeName>Kapitel i bok, del av antologi</publicationTypeName>
                    </publicationTypeName>
                    <publicationTypeName>
                        <publicationTypeNameId>242</publicationTypeNameId>
                        <locale>no</locale>
                        <publicationTypeName>Kapittel i bok, del av antologi</publicationTypeName>
                    </publicationTypeName>
                </publicationTypeNames>
                <roles />
                <comprehensiveSummary>false</comprehensiveSummary>
                <domainAdminOnly>false</domainAdminOnly>
            </publicationType>
            <pid>diva2:1270748</pid>
            <administrativeInfo>
                <domain>nordiskamuseet</domain>
                <creatorInfo>
                    <userId>mathilda.angkvist@nordiskamuseet.se</userId>
                    <ip>193.10.45.2</ip>
                    <name>Mathilda Ängkvist</name>
                    <date>2018-12-14T11:22:57.77901:00</date>
                    <userType>ADMIN</userType>
                    <userAction>CREATED</userAction>
                </creatorInfo>
                <createdDate>2018-12-14T11:22:57.77901:00</createdDate>
                <updatedDate>2025-06-12T18:41:53.88702:00</updatedDate>
            </administrativeInfo>
            <publicationDate>2018-12-14T11:22:57.69801:00</publicationDate>
            <originalPublicationTitle />
            <bookTitle />
            <publisher />
            <nbn>urn:nbn:se:nordiskamuseet:diva-1029</nbn>
            <oai>oai:DiVA.org:nordiskamuseet-1029</oai>
            <identifiers />
            <categories />
            <nationalCategories />
            <researchSubjects />
            <keyWords class="hashtable" />
            <abstracts>
                <abstract>
                    <language>
                        <languageCode3>-1</languageCode3>
                        <languageNames />
                        <showsOnList>false</showsOnList>
                    </language>
                </abstract>
            </abstracts>
            <artisticWork>false</artisticWork>
            <failed>false</failed>
            <hidden>false</hidden>
            <publicationOrder>
                <orderLink>false</orderLink>
                <validFrom>2018-12-14T11:22:54.34101:00</validFrom>
                <parameters />
            </publicationOrder>
            <canOrderOnline>false</canOrderOnline>
            <mediaInformation>
                <types />
                <materials />
                <techniques />
            </mediaInformation>
            <descriptions>
                <abstract>
                    <language>
                        <languageCode3>-1</languageCode3>
                        <languageNames />
                        <showsOnList>false</showsOnList>
                    </language>
                </abstract>
            </descriptions>
        </publication>
        """
    )

    result = transform_to_cora_output(
        fedora_xml,
        MockContext(),
    )

    assert_equal_for_xml_and_xml_string(
        result,
        """
        <output>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_book-chapter</linkedRecordId>
                </validationType>
                <dataDivider>
                    <linkedRecordType>system</linkedRecordType>
                    <linkedRecordId>divaData</linkedRecordId>
                </dataDivider>
                <permissionUnit>
                    <linkedRecordType>permissionUnit</linkedRecordType>
                    <linkedRecordId>nordiskamuseet</linkedRecordId>
                </permissionUnit>
                <visibility>published</visibility>
                <oldId>diva2:1270748</oldId>
                <urn>urn:nbn:se:nordiskamuseet:diva-1029</urn>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <genre type="outputType">publication_book-chapter</genre>
            <artisticWork type="outputType">false</artisticWork>
            <genre type="contentType">ref</genre>
        </output>                      
    """,
    )


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
