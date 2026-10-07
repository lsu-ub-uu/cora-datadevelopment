import pytest

from fedora_to_cora.authority_person_json_validate import (
    AuthorityPersonJSONValidationError,
    validate_authority_person_json,
)


def test_validate_authority_person_json_accepts_nested_arrays():
    document = {
        "authorityPerson": {
            "defaultName": {
                "lastname": "Andersson",
                "firstname": "Sara",
                "addition": "Professor",
                "number": "",
            },
            "alternativeNames": [
                {"lastname": "Tobiasson", "firstname": "Sara", "number": ""}
            ],
            "identifiers": [
                {
                    "type": "LOCAL",
                    "domain": "uu",
                    "value": "sarto903",
                    "from": "",
                    "until": "",
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
                            "organisationId": 978,
                            "domain": "uu",
                            "name": "Uppsala universitet",
                            "alternativeName": "Uppsala University",
                            "active": True,
                            "organisationNumber": "202100-2932-0",
                        }
                    ],
                }
            ],
            "urls": [{"label": "Homepage", "url": "https://example.test"}],
            "recordInfo": {
                "events": [
                    {
                        "type": "CREATE",
                        "timestamp": "2022-09-09T11:39:48.483Z",
                        "name": "Sara Tobiasson",
                        "userId": "sarto903",
                        "ip": "127.0.0.1",
                    }
                ],
                "recordDeleted": False,
            },
        }
    }

    validate_authority_person_json(document)


def test_validate_authority_person_maximal():
    document = {
        "authorityPerson": {
            "defaultName": {
                "lastname": "Andersson",
                "firstname": "Sara",
                "addition": "Professor",
                "number": "",
            },
            "birthYear": "1988",
            "email": "sara.tobiasson@user.uu.se",
            "alternativeNames": [
                {
                    "lastname": "Tobiasson",
                    "firstname": "Sara",
                    "number": "",
                },
                {
                    "lastname": "Andersson",
                    "firstname": "Anna",
                    "number": "",
                },
            ],
            "identifiers": [
                {
                    "type": "LIBRIS",
                    "domain": "",
                    "value": "2541478441254",
                    "from": "",
                    "until": "",
                },
                {
                    "type": "LOCAL",
                    "domain": "kau",
                    "value": "test123",
                    "from": "",
                    "until": "",
                },
                {
                    "type": "LOCAL",
                    "domain": "smhi",
                    "value": "test123",
                    "from": "",
                    "until": "",
                },
                {
                    "type": "LOCAL",
                    "domain": "uu",
                    "value": "sarto903",
                    "from": "",
                    "until": "",
                },
                {
                    "type": "ORCID",
                    "domain": "",
                    "value": "0000-1111-2222-3333",
                    "from": "",
                    "until": "",
                },
                {
                    "type": "VIAF",
                    "domain": "",
                    "value": "12aer458",
                    "from": "",
                    "until": "",
                },
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
                                    "active": True,
                                    "organisationNumber": "202100-2932-0",
                                }
                            ],
                            "active": True,
                            "organisationNumber": "",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "",
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
                                                    "active": True,
                                                    "organisationNumber": "202100-2932-0",
                                                }
                                            ],
                                            "active": True,
                                            "organisationNumber": "",
                                        }
                                    ],
                                    "active": True,
                                    "organisationNumber": "",
                                }
                            ],
                            "active": True,
                            "organisationNumber": "",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "",
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
                            "active": False,
                            "organisationNumber": "",
                        }
                    ],
                    "active": False,
                    "organisationNumber": "",
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
                                                    "active": True,
                                                    "organisationNumber": "202100-2932-0",
                                                }
                                            ],
                                            "active": True,
                                            "organisationNumber": "",
                                        }
                                    ],
                                    "active": True,
                                    "organisationNumber": "",
                                }
                            ],
                            "active": True,
                            "organisationNumber": "",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "",
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
                                    "active": False,
                                    "organisationNumber": "",
                                }
                            ],
                            "active": True,
                            "organisationNumber": "",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "123456-789",
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
                                    "active": True,
                                    "organisationNumber": "202100-2932-0",
                                }
                            ],
                            "active": True,
                            "organisationNumber": "",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "78596-985",
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
                            "active": True,
                            "organisationNumber": "202100-0696",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "",
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
                            "active": True,
                            "organisationNumber": "202100-2932-0",
                        }
                    ],
                    "active": True,
                    "organisationNumber": "",
                },
                {
                    "name": "Organsiation som fritext med ett årtal",
                    "alternativeName": "",
                    "from": "2025",
                    "active": False,
                    "organisationNumber": "",
                },
                {
                    "name": "En annan organisation med slutår",
                    "alternativeName": "",
                    "until": "2026",
                    "active": False,
                    "organisationNumber": "",
                },
            ],
            "urls": [
                {"label": "En url label", "url": "http://www.url.se"},
                {"label": "En annan url", "url": "http://www.enannanurl.se"},
            ],
            "biographies": {
                "eng": "<p><em>Min</em> biografi, <sup>en</sup> jätte <sub>lång</sub> text <em>med</em> olika <strong>formateringar</strong>. På engelska.</p>",
                "swe": "<p><strong>Min</strong> <em>biografi</em>, <sub>en</sub> jätte <sup>lång</sup> text med olika formateringar. På svenska.</p>",
            },
            "publicRecord": True,
            "type": "PERSON",
            "pid": "authority-person:11111",
            "recordInfo": {
                "events": [
                    {
                        "type": "CREATE",
                        "timestamp": "2022-09-09T11:39:48.483Z",
                        "name": "Sara Tobiasson",
                        "userId": "sarto903",
                        "ip": "130.238.90.152",
                    },
                    {
                        "type": "UPDATE",
                        "timestamp": "2022-09-09T11:41:01.964Z",
                        "name": "Sara Tobiasson",
                        "userId": "sarto903",
                        "ip": "130.238.90.152",
                    },
                ],
                "recordDeleted": False,
            },
        }
    }

    validate_authority_person_json(document)


def test_validate_authority_person_json_rejects_unknown_root_property():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match="Unknown property 'unknown' at root",
    ):
        validate_authority_person_json({"authorityPerson": {}, "unknown": "value"})


def test_validate_authority_person_json_rejects_unknown_array_item_property():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match=r"Unknown property 'unknown' at root.authorityPerson.identifiers\[0\]",
    ):
        validate_authority_person_json(
            {"authorityPerson": {"identifiers": [{"unknown": "value"}]}}
        )


def test_validate_authority_person_json_requires_array_for_repeated_property():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match="Expected a JSON array at root.authorityPerson.identifiers",
    ):
        validate_authority_person_json(
            {"authorityPerson": {"identifiers": {"type": "LOCAL"}}}
        )


def test_validate_authority_person_json_requires_object_array_items():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match=r"Expected a JSON object at root.authorityPerson.identifiers\[0\]",
    ):
        validate_authority_person_json(
            {"authorityPerson": {"identifiers": [[{"type": "LOCAL"}]]}}
        )


def test_validate_authority_person_json_rejects_object_for_scalar_property():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match="Expected a JSON string at root.authorityPerson.email",
    ):
        validate_authority_person_json(
            {"authorityPerson": {"email": {"value": "sara@example.test"}}}
        )


def test_validate_authority_person_json_rejects_non_boolean():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match="Expected a JSON boolean at root.authorityPerson.publicRecord",
    ):
        validate_authority_person_json({"authorityPerson": {"publicRecord": "true"}})


def test_validate_authority_person_json_rejects_non_number_organisation_id():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match=r"Expected a JSON number at root.authorityPerson.affiliations\[0\].organisationId",
    ):
        validate_authority_person_json(
            {"authorityPerson": {"affiliations": [{"organisationId": "12100"}]}}
        )


def test_validate_authority_person_json_requires_root_property():
    with pytest.raises(
        AuthorityPersonJSONValidationError,
        match="Missing required property 'authorityPerson' at root",
    ):
        validate_authority_person_json({})
