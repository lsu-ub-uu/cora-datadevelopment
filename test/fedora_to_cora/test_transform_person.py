from unittest.mock import Mock, patch
import json
from fedora_to_cora.transform_person import (
    transform_person,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_transform_minimal_person():
    minimal_old_person = json.loads("""{
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                  "pid": "authority-person:11111"
            }
        }""")

    transformed_person = transform_person(minimal_old_person)

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-person</linkedRecordId>
                </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>authority-person:11111</oldId>
            </recordInfo>
            <authority>
                <name type="personal">
                    <namePart type="given">David</namePart>
                    <namePart type="family">Andréasson</namePart>
                </name>
            </authority>
            </person>""",
    )


def test_transform_person_with_only_swe_biography():
    minimal_old_person = json.loads("""{
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                "biographies": {
                  "swe": "Hej hopp"
                },
                "pid": "authority-person:11111"
            }
        }""")

    transformed_person = transform_person(minimal_old_person)

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-person</linkedRecordId>
                </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>authority-person:11111</oldId>
            </recordInfo>
            <authority>
                <name type="personal">
                    <namePart type="given">David</namePart>
                    <namePart type="family">Andréasson</namePart>
                </name>
            </authority>
            <note type="biographical" lang="swe" repeatId="swe">Hej hopp</note>
            </person>""",
    )


def test_transform_person_ignores_identifier_without_value():
    minimal_old_person = json.loads("""{
            "authorityPerson": {
                "defaultName": {
                    "lastname": "Andréasson",
                    "firstname": "David",
                    "addition": "",
                    "number": ""
                },
                "identifiers":[
                  {
                    "type": "LIBRIS",
                    "domain": ""
                  },
                  {
                    "type": "ORCID",
                    "domain": "",
                    "value": "0000-1111-2222-3333",
                    "from": "",
                    "until": ""
                  }
                ],
                "pid": "authority-person:11111"
            }
        }""")

    transformed_person = transform_person(minimal_old_person)

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-person</linkedRecordId>
                </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>authority-person:11111</oldId>
            </recordInfo>
            <authority>
                <name type="personal">
                    <namePart type="given">David</namePart>
                    <namePart type="family">Andréasson</namePart>
                </name>
            </authority>
            <nameIdentifier type="orcid" repeatId="0">0000-1111-2222-3333</nameIdentifier>
            </person>""",
    )


@patch("fedora_to_cora.transform_person.get_cora_id_by_old_id")
def test_transform_maximal_person(mock_get_cora_id_by_old_id):

    mock_get_cora_id_by_old_id.side_effect = lambda old_id, **kwargs: "cora-" + old_id

    maximal_old_person = json.loads("""{
  "authorityPerson": {
    "defaultName": {
      "lastname": "Andersson",
      "firstname": "Sara",
      "addition": "Professor",
      "number": ""
    },
    "birthYear": "1988",
    "email": "sara.tobiasson@user.uu.se",
    "alternativeNames": [
      {
        "lastname": "Tobiasson",
        "firstname": "Sara",
        "addition": "",
        "number": ""
      },
      {
        "lastname": "Andersson",
        "firstname": "Anna",
        "addition": "",
        "number": ""
      }
    ],
    "identifiers": [
      {
        "type": "LIBRIS",
        "domain": "",
        "value": "2541478441254",
        "from": "",
        "until": ""
      },
      {
        "type": "LOCAL",
        "domain": "kau",
        "value": "test123",
        "from": "",
        "until": ""
      },
      {
        "type": "LOCAL",
        "domain": "smhi",
        "value": "test123",
        "from": "",
        "until": ""
      },
      {
        "type": "LOCAL",
        "domain": "uu",
        "value": "sarto903",
        "from": "",
        "until": ""
      },
      {
        "type": "ORCID",
        "domain": "",
        "value": "0000-1111-2222-3333",
        "from": "",
        "until": ""
      },
      {
        "type": "VIAF",
        "domain": "",
        "value": "12aer458",
        "from": "",
        "until": ""
      }
    ],
    "affiliations": [
      {
        "organisationId": 12100,
        "domain": "uu",
        "name": "IT-avdelningen",
        "alternativeName": "IT Division",
        "from": "2025",
        "parents": [
          {
            "organisationId": 979,
            "domain": "uu",
            "name": "Universitetsförvaltningen",
            "alternativeName": "University Administration",
            "parents": [
              {
                "organisationId": 978,
                "domain": "uu",
                "name": "Uppsala universitet",
                "alternativeName": "Uppsala University",
                "active": true,
                "organisationNumber": "202100-2932-0"
              }
            ],
            "active": true,
            "organisationNumber": ""
          }
        ],
        "active": true,
        "organisationNumber": ""
      },
      {
        "organisationId": 12102,
        "domain": "uu",
        "name": "Zooekologi",
        "alternativeName": "Animal ecology",
        "from": "2010",
        "until": "2011",
        "parents": [
          {
            "organisationId": 6800,
            "domain": "uu",
            "name": "Institutionen för ekologi och genetik",
            "alternativeName": "Department of Ecology and Genetics",
            "parents": [
              {
                "organisationId": 1112,
                "domain": "uu",
                "name": "Biologiska sektionen",
                "alternativeName": "Biology",
                "parents": [
                  {
                    "organisationId": 1031,
                    "domain": "uu",
                    "name": "Teknisk-naturvetenskapliga vetenskapsområdet",
                    "alternativeName": "Disciplinary Domain of Science and Technology",
                    "parents": [
                      {
                        "organisationId": 978,
                        "domain": "uu",
                        "name": "Uppsala universitet",
                        "alternativeName": "Uppsala University",
                        "active": true,
                        "organisationNumber": "202100-2932-0"
                      }
                    ],
                    "active": true,
                    "organisationNumber": ""
                  }
                ],
                "active": true,
                "organisationNumber": ""
              }
            ],
            "active": true,
            "organisationNumber": ""
          }
        ],
        "active": true,
        "organisationNumber": ""
      },
      {
        "organisationId": 2950,
        "domain": "uu",
        "name": "Avdelningen för Arkeologi och osteologi",
        "alternativeName": "Department of Archeology and Osteology",
        "from": "2015",
        "until": "2018",
        "parents": [
          {
            "organisationId": 2802,
            "domain": "uu",
            "name": "Högskolan på Gotland",
            "alternativeName": "Gotland University",
            "active": false,
            "organisationNumber": ""
          }
        ],
        "active": false,
        "organisationNumber": ""
      },
      {
        "organisationId": 7655,
        "domain": "uu",
        "name": "Växtekologi och evolution",
        "alternativeName": "Plant Ecology and Evolution",
        "from": "2025",
        "until": "2025",
        "parents": [
          {
            "organisationId": 6800,
            "domain": "uu",
            "name": "Institutionen för ekologi och genetik",
            "alternativeName": "Department of Ecology and Genetics",
            "parents": [
              {
                "organisationId": 1112,
                "domain": "uu",
                "name": "Biologiska sektionen",
                "alternativeName": "Biology",
                "parents": [
                  {
                    "organisationId": 1031,
                    "domain": "uu",
                    "name": "Teknisk-naturvetenskapliga vetenskapsområdet",
                    "alternativeName": "Disciplinary Domain of Science and Technology",
                    "parents": [
                      {
                        "organisationId": 978,
                        "domain": "uu",
                        "name": "Uppsala universitet",
                        "alternativeName": "Uppsala University",
                        "active": true,
                        "organisationNumber": "202100-2932-0"
                      }
                    ],
                    "active": true,
                    "organisationNumber": ""
                  }
                ],
                "active": true,
                "organisationNumber": ""
              }
            ],
            "active": true,
            "organisationNumber": ""
          }
        ],
        "active": true,
        "organisationNumber": ""
      },
      {
        "organisationId": 880751,
        "domain": "uu",
        "name": "test org 2 att tabort",
        "alternativeName": "test org 2 to remove",
        "from": "2021",
        "until": "2024",
        "parents": [
          {
            "organisationId": 880050,
            "domain": "uu",
            "name": "TESTTESTTEST",
            "alternativeName": "TESTTESTTEST - engrish",
            "parents": [
              {
                "organisationId": 2802,
                "domain": "uu",
                "name": "Högskolan på Gotland",
                "alternativeName": "Gotland University",
                "active": false,
                "organisationNumber": ""
              }
            ],
            "active": true,
            "organisationNumber": ""
          }
        ],
        "active": true,
        "organisationNumber": "123456-789"
      },
      {
        "organisationId": 878500,
        "domain": "uu",
        "name": "Testorganisation 1 att ta bort",
        "alternativeName": "Testorganisation 1 to remove",
        "from": "2024",
        "until": "2024",
        "parents": [
          {
            "organisationId": 985,
            "domain": "uu",
            "name": "Universitetsbiblioteket",
            "alternativeName": "University Library",
            "parents": [
              {
                "organisationId": 978,
                "domain": "uu",
                "name": "Uppsala universitet",
                "alternativeName": "Uppsala University",
                "active": true,
                "organisationNumber": "202100-2932-0"
              }
            ],
            "active": true,
            "organisationNumber": ""
          }
        ],
        "active": true,
        "organisationNumber": "78596-985"
      },
      {
        "organisationId": 872557,
        "domain": "smhi",
        "name": "Samhälle och säkerhet",
        "alternativeName": "Core Services",
        "parents": [
          {
            "organisationId": 16501,
            "domain": "smhi",
            "name": "SMHI",
            "alternativeName": "SMHI",
            "active": true,
            "organisationNumber": "202100-0696"
          }
        ],
        "active": true,
        "organisationNumber": ""
      },
      {
        "organisationId": 880800,
        "domain": "uu",
        "name": "Test test",
        "alternativeName": "Test test",
        "from": "2024",
        "until": "2025",
        "parents": [
          {
            "organisationId": 978,
            "domain": "uu",
            "name": "Uppsala universitet",
            "alternativeName": "Uppsala University",
            "active": true,
            "organisationNumber": "202100-2932-0"
          }
        ],
        "active": true,
        "organisationNumber": ""
      },
      {
        "name": "Organsiation som fritext med ett årtal",
        "alternativeName": "",
        "from": "2025",
        "active": false,
        "organisationNumber": ""
      },
      {
        "name": "En annan organisation med slutår",
        "alternativeName": "",
        "until": "2026",
        "active": false,
        "organisationNumber": ""
      }
    ],
    "urls": [
      {
        "label": "En url label",
        "url": "http://www.url.se"
      },
      {
        "label": "En annan url",
        "url": "http://www.enannanurl.se"
      }
    ],
    "biographies": {
      "eng": "<p><em>Min</em> biografi, <sup>en</sup> jätte <sub>lång</sub> text <em>med</em> olika <strong>formateringar</strong>. På engelska.</p>",
      "swe": "<p><strong>Min</strong> <em>biografi</em>, <sub>en</sub> jätte <sup>lång</sup> text med olika formateringar. På svenska.</p>"
    },
    "publicRecord": true,
    "type": "PERSON",
    "pid": "authority-person:11111",
    "recordInfo": {
      "events": [
        {
          "type": "CREATE",
          "timestamp": "2022-09-09T11:39:48.483Z",
          "name": "Sara Tobiasson",
          "userId": "sarto903",
          "ip": "130.238.90.152"
        },
        {
          "type": "UPDATE",
          "timestamp": "2022-09-09T11:41:01.964Z",
          "name": "Sara Tobiasson",
          "userId": "sarto903",
          "ip": "130.238.90.152"
        }
      ],
      "recordDeleted": false
    }
  }
}""")

    transformed_person = transform_person(maximal_old_person, context=Mock())

    assert_equal_for_xml_and_xml_string(
        transformed_person,
        """<person>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-person</linkedRecordId>
                </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>authority-person:11111</oldId>
            </recordInfo>
            <authority>
                <name type="personal">
                    <namePart type="given">Sara</namePart>
                    <namePart type="family">Andersson</namePart>
                    <namePart type="termsOfAddress">Professor</namePart>
                </name>
            </authority>
            <variant repeatId="0">
                <name type="personal">
                    <namePart type="given">Sara</namePart>
                    <namePart type="family">Tobiasson</namePart>
                </name>
            </variant>
            <variant repeatId="1">
                <name type="personal">
                    <namePart type="given">Anna</namePart>
                    <namePart type="family">Andersson</namePart>
                </name>
            </variant>
            <email repeatId="0">sara.tobiasson@user.uu.se</email>
            <location repeatId="0">
                <displayLabel>En url label</displayLabel>
                <url>http://www.url.se</url>
            </location>
            <location repeatId="1">
                <displayLabel>En annan url</displayLabel>
                <url>http://www.enannanurl.se</url>
            </location>
            <note type="biographical" lang="eng" repeatId="eng">Min biografi, en jätte lång text med olika formateringar. På engelska.</note>
            <note type="biographical" lang="swe" repeatId="swe">Min biografi, en jätte lång text med olika formateringar. På svenska.</note>
            <nameIdentifier type="localId" repeatId="0">test123</nameIdentifier>
            <nameIdentifier type="localId" repeatId="1">test123</nameIdentifier>
            <nameIdentifier type="localId" repeatId="2">sarto903</nameIdentifier>
            <nameIdentifier type="orcid" repeatId="0">0000-1111-2222-3333</nameIdentifier>
            <nameIdentifier repeatId="0" type="se-libr">2541478441254</nameIdentifier>
            <nameIdentifier type="viaf" repeatId="0">12aer458</nameIdentifier>
            <affiliation repeatId="0">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-12100</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2025</year>
                </startDate>
            </affiliation>
            <affiliation repeatId="1">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-12102</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2010</year>
                </startDate>
                <endDate>
                    <year>2011</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="2">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-2950</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2015</year>
                </startDate>
                <endDate>
                    <year>2018</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="3">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-7655</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2025</year>
                </startDate>
                <endDate>
                    <year>2025</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="4">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-880751</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2021</year>
                </startDate>
                <endDate>
                    <year>2024</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="5">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-878500</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2024</year>
                </startDate>
                <endDate>
                    <year>2024</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="6">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-872557</linkedRecordId>
                </organisation>
            </affiliation>
            <affiliation repeatId="7">
                <organisation>
                    <linkedRecordType>diva-organisation</linkedRecordType>
                    <linkedRecordId>cora-880800</linkedRecordId>
                </organisation>
                <startDate>
                    <year>2024</year>
                </startDate>
                <endDate>
                    <year>2025</year>
                </endDate>
            </affiliation>
            <affiliation repeatId="8">
                <namePart>Organsiation som fritext med ett årtal</namePart>
                <startDate>
                    <year>2025</year>
                </startDate>
            </affiliation>
            <affiliation repeatId="9">
                <namePart>En annan organisation med slutår</namePart>
                <endDate>
                    <year>2026</year>
                </endDate>
            </affiliation>
        </person>""",
    )


def test_transform_person_numbers_identifiers_per_type():
    old_person = {
        "authorityPerson": {
            "defaultName": {
                "firstname": "Sara",
                "lastname": "Andersson",
                "addition": "",
            },
            "pid": "authority-person:11111",
            "identifiers": [
                {"type": "LOCAL", "domain": "kau", "value": "test123"},
                {"type": "ORCID", "domain": "", "value": "0000-1111-2222-3333"},
                {"type": "LOCAL", "domain": "uu", "value": " "},
                {"type": "LIBRIS", "domain": "", "value": "2541478441254"},
                {"type": "LOCAL", "domain": "smhi", "value": "test123"},
                {"type": "VIAF", "domain": "", "value": "12aer458"},
                {"type": "ORCID", "domain": "", "value": "0000-4444-5555-6666"},
                {"type": "LOCAL", "domain": "uu", "value": "sarto903"},
            ],
        }
    }

    transformed_person = transform_person(old_person)

    identifiers = transformed_person.findall("nameIdentifier")
    assert [
        (identifier.attrib["type"], identifier.attrib["repeatId"])
        for identifier in identifiers
    ] == [
        ("localId", "0"),
        ("localId", "1"),
        ("localId", "2"),
        ("orcid", "0"),
        ("orcid", "1"),
        ("se-libr", "0"),
        ("viaf", "0"),
    ]
