from common.xml_validate import XMLSpec

fedora_authority_person_name_spec: XMLSpec = {
    "lastname": "$ANY_TEXT$",
    "firstname": "$ANY_TEXT$",
    "addition": "$ANY_TEXT$",
    "number": "$ANY_TEXT$",
}

fedora_authority_person_alternative_name_spec: XMLSpec = {
    "lastname": "$ANY_TEXT$",
    "firstname": "$ANY_TEXT$",
    "number": "$ANY_TEXT$",
}

fedora_authority_person_organisation_id_spec: XMLSpec = {
    "organisationId": "$NUMBER$",
}

fedora_authority_person_organisation_name_spec: XMLSpec = {
    "name": "$ANY_TEXT$",
    "alternativeName": "$ANY_TEXT$",
}

fedora_authority_person_organisation_spec: XMLSpec = {
    **fedora_authority_person_organisation_id_spec,
    **fedora_authority_person_organisation_name_spec,
    "domain": "$ANY_TEXT$",
    "active": "$BOOLEAN$",
    "organisationNumber": "$ANY_TEXT$",
}
fedora_authority_person_organisation_spec["parents"] = {
    **fedora_authority_person_organisation_spec,
}

fedora_authority_person_affiliation_spec: XMLSpec = {
    **fedora_authority_person_organisation_spec,
    "from": "$ANY_TEXT$",
    "until": "$ANY_TEXT$",
}

fedora_authority_person_spec: XMLSpec = {
    "defaultName": fedora_authority_person_name_spec,
    "birthYear": "$ANY_TEXT$",
    "email": "$ANY_TEXT$",
    "alternativeNames": fedora_authority_person_alternative_name_spec,
    "identifiers": {
        "type": "$ANY_TEXT$",
        "domain": "$ANY_TEXT$",
        "value": "$ANY_TEXT$",
        "from": "$ANY_TEXT$",
        "until": "$ANY_TEXT$",
    },
    "affiliations": fedora_authority_person_affiliation_spec,
    "urls": {
        "label": "$ANY_TEXT$",
        "url": "$ANY_TEXT$",
    },
    "biographies": {
        "eng": "$HTML$",
        "swe": "$HTML$",
    },
    "publicRecord": "$BOOLEAN$",
    "type": "$ANY_TEXT$",
    "pid": "$ANY_TEXT$",
    "recordInfo": {
        "events": {
            "type": "$ANY_TEXT$",
            "timestamp": "$ANY_TEXT$",
            "name": "$ANY_TEXT$",
            "userId": "$ANY_TEXT$",
            "ip": "$ANY_TEXT$",
        },
        "recordDeleted": "$BOOLEAN$",
    },
}
