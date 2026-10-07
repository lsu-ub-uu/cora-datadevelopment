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

logger = logging.getLogger(__name__)


def transform_person(old_person_record: dict) -> ET.Element:
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
            *[
                _create_variant(alternative_name)
                for alternative_name in old_person["alternativeNames"]
            ],
            _create_name_identifier(old_person, "localId"),
            _create_name_identifier(old_person, "orcid"),
            _create_name_identifier(old_person, "se-libr"),
            _create_name_identifier(old_person, "viaf"),
            _create_affiliation(old_person),
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
    given_name = get_first_atomic_value_with_name_in_data(
        old_person["defaultName"]["firstname"], "givenName"
    )
    last_name = get_first_atomic_value_with_name_in_data(
        old_person["defaultName"]["lastname"], "familyName"
    )

    return create_group(
        "authority",
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text("namePart", given_name, type="given"),
                    create_text("namePart", last_name, type="family"),
                ],
            )
        ],
    )


def _create_variant(alternative_name: dict):
    given_name = get_first_atomic_value_with_name_in_data(
        old_person["alternativeNames"]["firstname"], "givenName"
    )
    last_name = get_first_atomic_value_with_name_in_data(
        old_person["alternativeNames"]["lastname"], "familyName"
    )

    return create_group(
        "variant",
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text("namePart", given_name, type="given"),
                    create_text("namePart", last_name, type="family"),
                ],
            )
        ],
    )


""" def _create_note_sv(old_person: dict):
    return create_text(
        "note", old_person["biographies"]["swe"], type="biographical", lang="sv"
    )
 """


def _create_name_identifier(old_person_data: dict, type: str):
    value = get_first_atomic_value_with_name_in_data(
        old_person_data["children"],
        "ORCID_ID",
    )
    return create_text(
        "nameIdentifier",
        value=value,
        type=type,
    )


def _create_affiliation(old_person_data: dict):
    pass
