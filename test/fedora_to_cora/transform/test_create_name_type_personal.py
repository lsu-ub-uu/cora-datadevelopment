from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_name_type_personal import (
    create_degree_supervisor,
    create_name_type_personals,
    create_opponents,
    create_thesis_advisor,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext

mock_context = MockContext("https://example.org/rest/record/", "test-token")


def test_creates_name_type_personal():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>      
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
        </name>
        """,
    )


def test_creates_name_type_personal_birth_year():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>      
                    <birthYear>1802</birthYear>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <namePart type="date">1802</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
        </name>
        """,
    )


def test_creates_name_type_personal_death_year():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>      
                    <deathYear>1802</deathYear>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <namePart type="date">-1802</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
        </name>
        """,
    )


def test_creates_name_type_personal_birth_and_death_year():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>      
                    <birthYear>1802</birthYear>
                    <deathYear>1977</deathYear>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <namePart type="date">1802-1977</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
        </name>
        """,
    )


def test_creates_persons_for_roles():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Abel</firstName>
                    <lastName>The Author</lastName>
                </person>
            </authors>
            <editors>
                <person>
                    <firstName>Beata</firstName>
                    <lastName>The Editor</lastName>
                </person>
            </editors>
            <examiners>
                <person>
                    <firstName>Cecil</firstName>
                    <lastName>The Examiner</lastName>
                </person>
            </examiners>
            <supervisors>
                <person>
                    <firstName>Diana</firstName>
                    <lastName>The Supervisor</lastName>
                </person>
            </supervisors>
            <opponents>
                <person>
                    <firstName>Egil</firstName>
                    <lastName>The Opponent</lastName>
                </person>
            </opponents>
            <otherContributors>
                <contributor>
                    <firstName>Fiona</firstName>
                    <lastName>The Woodcutter</lastName>
                    <roles>
                        <role><marcCode>wdc</marcCode></role>
                        <role><marcCode>act</marcCode></role>
                    </roles>
                </contributor>
                <contributor>
                    <firstName>Gunnar</firstName>
                    <lastName>The Dancer</lastName>
                    <roles>
                        <role><marcCode>dnc</marcCode></role>
                    </roles>
                </contributor>
            </otherContributors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )

    assert len(names) == 4

    abel = names[0].find("./role/roleTerm")
    assert abel is not None and abel.text == "aut"

    beata = names[1].find("./role/roleTerm")
    assert beata is not None and beata.text == "edt"

    fiona = names[2].findall("./role/roleTerm")
    assert len(fiona) == 2
    assert fiona[0].text == "wdc"
    assert fiona[1].text == "act"

    gunnar = names[3].find("./role/roleTerm")
    assert gunnar is not None and gunnar.text == "dnc"


def test_creates_uncontrolled_affiliation():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>
                    <organisations>
                        <organisation>
                            <organisationNameUncontrolled>Extern organisation</organisationNameUncontrolled>
                            <controlled>false</controlled>
                        </organisation>
                    </organisations>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <affiliation repeatId="0">
                <namePart>Extern organisation</namePart>
            </affiliation>
        </name>
        """,
    )


def test_creates_controlled_affiliation(monkeypatch):
    mock_old_id = "985"
    expected_cora_id = "diva-organisation:21861441014837120"

    def mock_get_org(old_id, *args, **kwargs):
        if old_id == mock_old_id:
            return expected_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.create_name_type_personal.get_cora_id_by_old_id",
        mock_get_org,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>
                    <organisations>
                        <organisation>
                            <organisationId>{mock_old_id}</organisationId>
                            <controlled>true</controlled>
                        </organisation>
                    </organisations>
                </person>
            </authors>
        </publication>
        """
    )

    names = create_name_type_personals(
        source_record,
        mock_context,
    )

    assert_equal_for_xml_and_xml_string(
        names[0],
        f"""
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <affiliation repeatId="0">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>{expected_cora_id}</linkedRecordId>
                </organisation>
            </affiliation>
        </name>
        """,
    )


def test_creates_for_author_only_validation_type():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>65</publicationTypeId>
                <publicationTypeCode>studentThesis</publicationTypeCode>
                <publicationTypeCode>diva_degree-project</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>John</firstName>
                    <lastName>Doe</lastName>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Doe</namePart>
            <namePart type="given">John</namePart>
            <role><roleTerm>aut</roleTerm></role>
        </name>
        """,
    )


def test_create_supervisors():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <supervisors>
                <person>
                    <firstName>Sarah</firstName>
                    <lastName>Smith</lastName>
                    <organisations>
                        <organisation>
                            <organisationNameUncontrolled>Extern organisation</organisationNameUncontrolled>
                            <controlled>false</controlled>
                        </organisation>
                    </organisations>
                </person>
                <person>
                    <firstName>Karah</firstName>
                    <lastName>Kmith</lastName>
                </person>
            </supervisors>
        </publication>
        """
    )
    names = create_thesis_advisor(
        source_record,
        mock_context,
    )

    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" otherType="thesisAdvisor" repeatId="0">
            <namePart type="family">Smith</namePart>
            <namePart type="given">Sarah</namePart>
            <role><roleTerm repeatId="0">ths</roleTerm></role>
            <affiliation repeatId="0">
                <namePart>Extern organisation</namePart>
            </affiliation>
        </name>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        names[1],
        """
        <name type="personal" otherType="thesisAdvisor" repeatId="1">
            <namePart type="family">Kmith</namePart>
            <namePart type="given">Karah</namePart>
            <role><roleTerm repeatId="0">ths</roleTerm></role>
        </name>
        """,
    )


def test_create_opponents():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <opponents>
                <person>
                    <firstName>Oliver</firstName>
                    <lastName>Olsen</lastName>
                </person>
            </opponents>
        </publication>
        """
    )
    names = create_opponents(
        source_record,
        mock_context,
    )

    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" otherType="opponent" repeatId="0">
            <namePart type="family">Olsen</namePart>
            <namePart type="given">Oliver</namePart>
            <role><roleTerm repeatId="0">opn</roleTerm></role>
        </name>
        """,
    )


def test_create_examiners():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <examiners>
                <person>
                    <firstName>Erik</firstName>
                    <lastName>Eriksson</lastName>
                </person>
            </examiners>
        </publication>
        """
    )
    names = create_degree_supervisor(
        source_record,
        mock_context,
    )

    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" otherType="degreeSupervisor" repeatId="0">
            <namePart type="family">Eriksson</namePart>
            <namePart type="given">Erik</namePart>
            <role><roleTerm repeatId="0">dgs</roleTerm></role>
        </name>
        """,
    )


def test_creates_name_identifiers():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>
                    <localId>aaaa111</localId>
                    <identifiers>
                        <entry>
                        <personIdentifierType>orcid</personIdentifierType>
                        <personIdentifier>
                            <value>0000-0002-3134-8865</value>
                            <type>orcid</type>
                        </personIdentifier>
                        </entry>
                    </identifiers>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <nameIdentifier type="localId">aaaa111</nameIdentifier>
            <nameIdentifier type="orcid">0000-0002-3134-8865</nameIdentifier>
        </name>
        """,
    )


def test_other_contributor_without_role():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <otherContributors>
                <contributor>
                    <firstName>Fiona</firstName>
                    <lastName>The Roleless</lastName>
                    <identifiers>
                        <entry>
                        <personIdentifierType>orcid</personIdentifierType>
                        <personIdentifier>
                            <value />
                            <type>orcid</type>
                        </personIdentifier>
                        </entry>
                    </identifiers>
                </contributor>
            </otherContributors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )

    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">The Roleless</namePart>
            <namePart type="given">Fiona</namePart>
        </name>
        """,
    )


def test_creates_affiliation_from_research_group():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>
                    <researchGroup>Forskargänget</researchGroup>
                </person>
            </authors>
        </publication>
        """
    )

    names = create_name_type_personals(
        source_record,
        mock_context,
    )

    assert len(names) == 1

    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <affiliation repeatId="0">
                <namePart>Forskargänget</namePart>
                <description>researchGroup</description>
            </affiliation>
        </name>
        """,
    )


def test_replaces_lowercase_x_in_orcid():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
                <publicationTypeCode>collection</publicationTypeCode>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Schmanderson</lastName>
                    <identifiers>
                        <entry>
                            <personIdentifierType>orcid</personIdentifierType>
                            <personIdentifier>
                                <value>0000-0002-3134-886x</value>
                                <type>orcid</type>
                            </personIdentifier>
                        </entry>
                    </identifiers>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(
        source_record,
        mock_context,
    )
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Schmanderson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <nameIdentifier type="orcid">0000-0002-3134-886X</nameIdentifier>
        </name>
        """,
    )
