import logging
from typing import Any
import requests
from xml.etree import ElementTree as ET

from common.common_data import create_record_link
from common.xml_utils import create_group, create_text
from cora.context import Context
from cora.cora_json_utils import (
    find_child_with_name_in_data,
    get_first_atomic_value_with_name_in_data,
)
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from fedora_to_cora.clean_rich_text import clean_rich_text

logger = logging.getLogger(__name__)


def transform_person(
    old_person_record: dict, context: Context | None = None
) -> ET.Element:
    old_person = old_person_record["authorityPerson"]
    person = create_group(
        "person",
        children=[
            create_group(
                "recordInfo",
                children=[
                    _create_validation_type(),
                    _create_data_divider(),
                    _create_old_id(old_person),
                ],
            ),
            _create_authority(old_person),
            _create_variants(old_person),
            _create_email(old_person),
            _create_location(old_person),
            _create_note(old_person, "eng"),
            _create_note(old_person, "swe"),
            _create_name_identifier(old_person),
            _create_affiliation(old_person, context),
        ],
    )
    assert person is not None
    return person


def _create_validation_type():
    return create_record_link("validationType", "validationType", "diva-person")


def _create_data_divider():
    return create_record_link("dataDivider", "system", "divaData")


def _create_old_id(old_person: dict):
    return create_text(
        "oldId",
        old_person["pid"],
    )


def _create_authority(old_person: dict):
    given_name = old_person["defaultName"]["firstname"]
    last_name = old_person["defaultName"]["lastname"]
    address = old_person["defaultName"]["addition"]

    return create_group(
        "authority",
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text("namePart", given_name, type="given"),
                    create_text("namePart", last_name, type="family"),
                    create_text("namePart", address, type="termsOfAddress"),
                ],
            )
        ],
    )


def _create_variants(old_person: dict):
    return [
        _create_variant(alternative_name, str(index))
        for index, alternative_name in enumerate(
            old_person["alternativeNames"] if "alternativeNames" in old_person else []
        )
    ]


def _create_variant(alternative_name: dict, repeat_id: str):
    return create_group(
        "variant",
        repeatId=str(repeat_id),
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text(
                        "namePart", alternative_name["firstname"], type="given"
                    ),
                    create_text(
                        "namePart", alternative_name["lastname"], type="family"
                    ),
                ],
            )
        ],
    )


def _create_email(old_person_data: dict):
    email = old_person_data["email"] if "email" in old_person_data else ""
    if email:
        return create_text("email", repeatId="0", value=email)
    return None


def _create_location(old_person: dict):
    locations = []
    for repeat_id, url_entry in enumerate(
        old_person["urls"] if "urls" in old_person else []
    ):
        locations.append(
            create_group(
                "location",
                repeatId=str(repeat_id),
                children=[
                    create_text("displayLabel", url_entry["label"]),
                    create_text("url", url_entry["url"]),
                ],
            )
        )
    return locations


def _create_note(old_person: dict, lang: str):
    if "biographies" not in old_person or lang not in old_person["biographies"]:
        return None

    return create_text(
        "note",
        repeatId=lang,
        type="biographical",
        lang=lang,
        value=clean_rich_text(old_person["biographies"][lang]),
    )


def _create_name_identifier(old_person_data: dict):
    name_identifiers = []
    identifier_types = [
        ("localId", "LOCAL"),
        ("orcid", "ORCID"),
        ("se-libr", "LIBRIS"),
        ("viaf", "VIAF"),
    ]
    identifiers = (
        old_person_data["identifiers"] if "identifiers" in old_person_data else []
    )
    for type, source_type in identifier_types:
        for identifier in identifiers:
            if "value" not in identifier or "type" not in identifier:
                continue

            if identifier["type"] != source_type:
                continue
            value = identifier["value"]

            name_identifier = create_text(
                "nameIdentifier",
                value=value,
                type=type,
                repeatId=str(
                    sum(1 for item in name_identifiers if item.attrib["type"] == type)
                ),
            )
            if name_identifier is not None:
                name_identifiers.append(name_identifier)

    return name_identifiers


def _create_affiliation(old_person_data: dict, context: Context | None = None):
    affiliations = []
    for repeat_id, affiliation in enumerate(
        old_person_data["affiliations"] if "affiliations" in old_person_data else []
    ):
        organisation_id = (
            affiliation["organisationId"] if "organisationId" in affiliation else None
        )
        if organisation_id is not None:
            organisation_or_name = _create_organisation(organisation_id, context)
        else:
            organisation_or_name = _create_name(affiliation)

        affiliations.append(
            create_group(
                "affiliation",
                repeatId=str(repeat_id),
                children=[
                    organisation_or_name,
                    create_group(
                        "startDate",
                        children=[
                            create_text(
                                "year",
                                affiliation["from"] if "from" in affiliation else None,
                            )
                        ],
                    ),
                    create_group(
                        "endDate",
                        children=[
                            create_text(
                                "year",
                                (
                                    affiliation["until"]
                                    if "until" in affiliation
                                    else None
                                ),
                            )
                        ],
                    ),
                ],
            )
        )
    return affiliations


def _create_organisation(organisation_id: int, context: Context | None):
    if context is None:
        raise ValueError(
            "A Cora context is required to resolve organisation affiliations."
        )
    return create_record_link(
        "organisation",
        "diva-organisation",
        get_cora_id_by_old_id(
            str(organisation_id),
            record_type="diva-organisation",
            context=context,
        ),
    )


def _create_name(affiliation: dict):
    return create_text("namePart", affiliation["name"])
