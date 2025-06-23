from xml.etree import ElementTree as ET
from fedora_to_cora import create_name_type_personals
from common.test_helper import assert_equal_for_xml_and_xml_string

source_record = ET.fromstring(
    """
    <publication>
        <authors>
            <person>
                <firstName>Michaela</firstName>
                <lastName>Andersson</lastName>
                <localId>mican434</localId>
                <organisations>
                    <organisation>
                    <organisationContacts/>
                    <organisationPredecessors/>
                    <organisationPredecessorDescriptions/>
                    <organisationNameUncontrolled>Extern organisation</organisationNameUncontrolled>
                    <controlled>false</controlled>
                    <notEligible>false</notEligible>
                    <showInPortal>false</showInPortal>
                    <showInDefence>false</showInDefence>
                    <topLevel>false</topLevel>
                    </organisation>
                    <organisation>
                    <organisationId>985</organisationId>
                    <organisationType>
                        <organisationTypeId>55</organisationTypeId>
                        <organisationTypeCode>unit</organisationTypeCode>
                        <organisationTypeNames>
                        <organisationTypeName>
                            <organisationTypeNameId>1911</organisationTypeNameId>
                            <locale>en</locale>
                            <organisationTypeName>Unit</organisationTypeName>
                        </organisationTypeName>
                        <organisationTypeName>
                            <organisationTypeNameId>1910</organisationTypeNameId>
                            <locale>sv</locale>
                            <organisationTypeName>Enhet</organisationTypeName>
                        </organisationTypeName>
                        </organisationTypeNames>
                    </organisationType>
                    <organisationName>
                        <name>Universitetsbiblioteket</name>
                        <locale>sv</locale>
                    </organisationName>
                    <domain>uu</domain>
                    <oldDivaDb>uu</oldDivaDb>
                    <oldDivaId>701</oldDivaId>
                    <oldParentId>4569</oldParentId>
                    <organisationAlternativeNames>
                        <organisationName>
                        <organisationNameId>2716</organisationNameId>
                        <locale>en</locale>
                        <organisationName>University Library</organisationName>
                        </organisationName>
                    </organisationAlternativeNames>
                    <organisationContacts/>
                    <organisationAddress>
                        <addressId>1961</addressId>
                        <postbox>Box 510</postbox>
                        <postnumber>75120</postnumber>
                        <city>Uppsala</city>
                        <country>
                        <countryCode>se</countryCode>
                        <countryNames>
                            <countryName>
                            <countryNameId>775</countryNameId>
                            <locale>sv</locale>
                            <countryName>Sverige</countryName>
                            </countryName>
                            <countryName>
                            <countryNameId>774</countryNameId>
                            <locale>en</locale>
                            <countryName>Sweden</countryName>
                            </countryName>
                            <countryName>
                            <countryNameId>10553</countryNameId>
                            <locale>no</locale>
                            <countryName>Sverige</countryName>
                            </countryName>
                        </countryNames>
                        <showsOnList>true</showsOnList>
                        </country>
                    </organisationAddress>
                    <organisationParents>
                        <organisation>
                        <organisationId>978</organisationId>
                        <organisationType>
                            <organisationTypeId>50</organisationTypeId>
                            <organisationTypeCode>university</organisationTypeCode>
                            <organisationTypeNames>
                            <organisationTypeName>
                                <organisationTypeNameId>1901</organisationTypeNameId>
                                <locale>en</locale>
                                <organisationTypeName>University</organisationTypeName>
                            </organisationTypeName>
                            <organisationTypeName>
                                <organisationTypeNameId>1900</organisationTypeNameId>
                                <locale>sv</locale>
                                <organisationTypeName>Universitet</organisationTypeName>
                            </organisationTypeName>
                            </organisationTypeNames>
                        </organisationType>
                        <organisationName>
                            <name>Uppsala universitet</name>
                            <locale>sv</locale>
                        </organisationName>
                        <domain>uu</domain>
                        <organisationNumber>202100-2932-0</organisationNumber>
                        <oldDivaDb>uu</oldDivaDb>
                        <oldDivaId>4569</oldDivaId>
                        <organisationAlternativeNames>
                            <organisationName>
                            <organisationNameId>2709</organisationNameId>
                            <locale>en</locale>
                            <organisationName>Uppsala University</organisationName>
                            </organisationName>
                        </organisationAlternativeNames>
                        <organisationContacts/>
                        <organisationAddress>
                            <addressId>1956</addressId>
                            <postnumber>75105</postnumber>
                            <city>Uppsala</city>
                            <country>
                            <countryCode>se</countryCode>
                            <countryNames>
                                <countryName>
                                <countryNameId>775</countryNameId>
                                <locale>sv</locale>
                                <countryName>Sverige</countryName>
                                </countryName>
                                <countryName>
                                <countryNameId>774</countryNameId>
                                <locale>en</locale>
                                <countryName>Sweden</countryName>
                                </countryName>
                                <countryName>
                                <countryNameId>10553</countryNameId>
                                <locale>no</locale>
                                <countryName>Sverige</countryName>
                                </countryName>
                            </countryNames>
                            <showsOnList>true</showsOnList>
                            </country>
                        </organisationAddress>
                        <organisationParents>
                            <organisation>
                            <organisationId>6599</organisationId>
                            <organisationType>
                                <organisationTypeId>49</organisationTypeId>
                                <organisationTypeCode>root</organisationTypeCode>
                                <organisationTypeNames>
                                <organisationTypeName>
                                    <organisationTypeNameId>1925</organisationTypeNameId>
                                    <locale>en</locale>
                                    <organisationTypeName>Root organisation</organisationTypeName>
                                </organisationTypeName>
                                <organisationTypeName>
                                    <organisationTypeNameId>1924</organisationTypeNameId>
                                    <locale>sv</locale>
                                    <organisationTypeName>Rotorganisation</organisationTypeName>
                                </organisationTypeName>
                                </organisationTypeNames>
                            </organisationType>
                            <organisationName>
                                <name>UU</name>
                                <locale>sv</locale>
                            </organisationName>
                            <domain>uu</domain>
                            <organisationAlternativeNames>
                                <organisationName>
                                <organisationNameId>51963</organisationNameId>
                                <locale>en</locale>
                                <organisationName>UU</organisationName>
                                </organisationName>
                            </organisationAlternativeNames>
                            <organisationContacts/>
                            <organisationParents/>
                            <organisationPredecessors/>
                            <organisationPredecessorDescriptions/>
                            <controlled>true</controlled>
                            <notEligible>true</notEligible>
                            <showInPortal>false</showInPortal>
                            <showInDefence>false</showInDefence>
                            <topLevel>false</topLevel>
                            </organisation>
                        </organisationParents>
                        <organisationPredecessors/>
                        <organisationPredecessorDescriptions/>
                        <controlled>true</controlled>
                        <notEligible>false</notEligible>
                        <showInPortal>true</showInPortal>
                        <showInDefence>true</showInDefence>
                        <topLevel>true</topLevel>
                        </organisation>
                    </organisationParents>
                    <organisationPredecessors/>
                    <organisationPredecessorDescriptions/>
                    <controlled>true</controlled>
                    <notEligible>false</notEligible>
                    <showInPortal>false</showInPortal>
                    <showInDefence>false</showInDefence>
                    <topLevel>false</topLevel>
                    </organisation>
                </organisations>
                <email>epost@adress.se</email>
                <birthYear>1802</birthYear>
                <deathYear>1977</deathYear>
                <title>Jägmästare</title>
                <researchGroup>En forskargrupp</researchGroup>
                <identifiers>
                    <entry>
                    <personIdentifierType>orcid</personIdentifierType>
                    <personIdentifier>
                        <value>0000-0002-3134-8865</value>
                        <type>orcid</type>
                    </personIdentifier>
                    </entry>
                    <entry>
                    <personIdentifierType>viaf</personIdentifierType>
                    <personIdentifier>
                        <value>66470391</value>
                        <type>viaf</type>
                    </personIdentifier>
                    </entry>
                    <entry>
                    <personIdentifierType>libris</personIdentifierType>
                    <personIdentifier>
                        <value>khwz2wc314fjgq3</value>
                        <type>libris</type>
                    </personIdentifier>
                    </entry>
                </identifiers>
                <authorityPid>authority-person:60563</authorityPid>
            </person>
            <person>
                <firstName>Per</firstName>
                <lastName>Minimal</lastName>
                <identifiers>
                    <entry>
                    <personIdentifierType>orcid</personIdentifierType>
                    <personIdentifier>
                        <value/>
                        <type>orcid</type>
                    </personIdentifier>
                    </entry>
                </identifiers>
            </person>
            <person>
                <firstName>Mats</firstName>
                <lastName>Mellanting</lastName>
                <localId>mellan02</localId>
                <organisations>
                    <organisation>
                    <organisationContacts/>
                    <organisationPredecessors/>
                    <organisationPredecessorDescriptions/>
                    <organisationNameUncontrolled>Annat universitet</organisationNameUncontrolled>
                    <controlled>false</controlled>
                    <notEligible>false</notEligible>
                    <showInPortal>false</showInPortal>
                    <showInDefence>false</showInDefence>
                    <topLevel>false</topLevel>
                    </organisation>
                </organisations>
                <identifiers>
                    <entry>
                    <personIdentifierType>orcid</personIdentifierType>
                    <personIdentifier>
                        <value>0000-7777-0000-000X</value>
                        <type>orcid</type>
                    </personIdentifier>
                    </entry>
                </identifiers>
            </person>
        </authors>
    </publication>
    """
)

# <name type="personal">
#     <person />
#     <namePart type="family"/>
#     <namePart type="given" />
#     <role>
#         <roleTerm />
#     <affiliation>
#         <organisation />
#         <name type="corporate" />
#             <namePart />
#         <identifier type="ror" />
#         <country />
#         <description />
#     </ affiliation>
# </name>


def test_creates_name_type_personal():
    source_record = ET.fromstring(
        """
        <publication>
            <authors>
                <person>
                    <firstName>Michaela</firstName>
                    <lastName>Andersson</lastName>
                </person>
            </authors>
        </publication>
        """
    )
    names = create_name_type_personals(source_record)
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Andersson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm type="code" repeatId="0">aut</roleTerm></role>
        </name>
        """,
    )


def test_creates_persons_for_roles():
    source_record = ET.fromstring(
        """
        <publication>
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
    names = create_name_type_personals(source_record)

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
    names = create_name_type_personals(source_record)
    assert_equal_for_xml_and_xml_string(
        names[0],
        """
        <name type="personal" repeatId="0">
            <namePart type="family">Andersson</namePart>
            <namePart type="given">Michaela</namePart>
            <role><roleTerm type="code" repeatId="0">aut</roleTerm></role>
            <affiliation repeatId="0">
                <name type="corporate">
                    <namePart>Extern organisation</namePart>
                </name>
            </affiliation>
        </name>
        """,
    )
