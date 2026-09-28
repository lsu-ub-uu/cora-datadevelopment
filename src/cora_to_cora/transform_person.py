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


def transform_person(old_person: dict, context: Context | None = None) -> ET.Element:
    old_person_data = old_person["record"]["data"]
    old_record_info = find_child_with_name_in_data(
        old_person_data["children"], "recordInfo"
    )
    assert old_record_info is not None
    person = create_group(
        "person",
        children=[
            create_group(
                "recordInfo",
                children=[
                    _create_validation_type(),
                    _create_data_divider(),
                    _create_old_id(old_record_info),
                ],
            ),
            _create_authority(old_person_data),
            _create_variant(old_person_data),
            _create_name_identifier(old_person_data, "orcid"),
            _create_affiliation(old_person_data, context),
        ],
    )
    assert person is not None
    return person


def _create_validation_type():
    return create_record_link("validationType", "validationType", "diva-person")


def _create_data_divider():
    return create_record_link("dataDivider", "system", "divaData")


def _create_old_id(old_record_info: dict):
    return create_text(
        "oldId",
        get_first_atomic_value_with_name_in_data(old_record_info["children"], "id"),
    )


def _create_authority(old_person_data: dict):
    authorised_name = find_child_with_name_in_data(
        old_person_data["children"], "authorisedName"
    )
    if authorised_name is None:
        return None

    given_name = get_first_atomic_value_with_name_in_data(
        authorised_name["children"], "givenName"
    )
    family_name = get_first_atomic_value_with_name_in_data(
        authorised_name["children"], "familyName"
    )

    return create_group(
        "authority",
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text("namePart", given_name, type="given"),
                    create_text("namePart", family_name, type="family"),
                ],
            )
        ],
    )


def _create_variant(old_person_data: dict):
    alternative_name = find_child_with_name_in_data(
        old_person_data["children"], "alternativeName"
    )
    if alternative_name is None:
        return None

    given_name = get_first_atomic_value_with_name_in_data(
        alternative_name["children"], "givenName"
    )
    family_name = get_first_atomic_value_with_name_in_data(
        alternative_name["children"], "familyName"
    )

    return create_group(
        "variant",
        children=[
            create_group(
                "name",
                type="personal",
                children=[
                    create_text("namePart", given_name, type="given"),
                    create_text("namePart", family_name, type="family"),
                ],
            )
        ],
    )


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


def _create_affiliation(old_person_data: dict, context: Context | None):
    person_domain_part = find_child_with_name_in_data(
        old_person_data["children"], "personDomainPart"
    )
    if person_domain_part is None:
        return None

    person_domain_part_id = get_first_atomic_value_with_name_in_data(
        person_domain_part["children"], "linkedRecordId"
    )

    assert (
        person_domain_part_id is not None
    ), "Affiliation found but no linkedRecordId present in the personDomainPart data"

    cora_organisation_id = _get_organisation_id_from_person_domain_part_id(
        person_domain_part_id, context
    )

    return create_group(
        "affiliation",
        children=[
            create_group(
                "organisation",
                children=[
                    create_text("linkedRecordType", "diva-organisation"),
                    create_text("linkedRecordId", cora_organisation_id),
                ],
            )
        ],
    )


def _get_organisation_id_from_person_domain_part_id(
    person_domain_part_id: str, context: Context | None
):
    if context is None:
        raise ValueError(
            "Context is required to resolve organisation id from personDomainPart"
        )

    person_domain_part_data = _get_person_domain_part(context, person_domain_part_id)
    affiliation = find_child_with_name_in_data(
        person_domain_part_data["children"], "affiliation"
    )

    assert (
        affiliation is not None
    ), "Person domain part did not contain an organisation link"

    organisation_link = find_child_with_name_in_data(
        affiliation["children"], "organisationLink"
    )
    assert (
        organisation_link is not None
    ), "Person domain part did not contain an organisationLink"

    classic_organisation_id = get_first_atomic_value_with_name_in_data(
        organisation_link["children"], "linkedRecordId"
    )
    assert (
        classic_organisation_id is not None
    ), "Person domain part organisationLink did not contain a linkedRecordId"

    return get_cora_id_by_old_id(
        classic_organisation_id,
        record_type="diva-organisation",
        context=context,
    )


def _get_person_domain_part(
    context: Context, person_domain_part_id: str
) -> dict[str, Any]:
    request_url = f"{context.get_base_url()}personDomainPart/{person_domain_part_id}"
    headers = {
        "Accept": "application/json",
        "authToken": context.get_auth_token(),
    }

    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(
            f"❌ An error occurred while fetching personDomainPart with id {person_domain_part_id}: {str(e)}"
        )
        raise e
