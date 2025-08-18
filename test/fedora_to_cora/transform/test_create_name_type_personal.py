from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_name_type_personal import (
    create_name_type_personals,
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
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Andersson</lastName>
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
            <namePart type="family">Andersson</namePart>
            <namePart type="given">Michaela</namePart>
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

    assert len(names) == 7

    abel = names[0].find("./role/roleTerm")
    assert abel is not None and abel.text == "aut"

    beata = names[1].find("./role/roleTerm")
    assert beata is not None and beata.text == "edt"

    cecil = names[2].find("./role/roleTerm")
    assert cecil is not None and cecil.text == "dgs"

    diana = names[3].find("./role/roleTerm")
    assert diana is not None and diana.text == "ths"

    egil = names[4].find("./role/roleTerm")
    assert egil is not None and egil.text == "opn"

    fiona = names[5].findall("./role/roleTerm")
    assert len(fiona) == 2
    assert fiona[0].text == "wdc"
    assert fiona[1].text == "act"

    gunnar = names[6].find("./role/roleTerm")
    assert gunnar is not None and gunnar.text == "dnc"


def test_creates_uncontrolled_affiliation():
    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeId>63</publicationTypeId>
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Andersson</lastName>
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
            <namePart type="family">Andersson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm repeatId="0">aut</roleTerm></role>
            <affiliation repeatId="0">
                <name type="corporate">
                    <namePart>Extern organisation</namePart>
                </name>
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
            </publicationType>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Andersson</lastName>
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
            <namePart type="family">Andersson</namePart>
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
