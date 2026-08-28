from cora.context import Context
from xml.etree import ElementTree as ET
from common.common_data import create_record_link
from common.xml_utils import append_if_value, create_group, create_text
from cora.cora_json_utils import (
    get_first_atomic_value_with_name_in_data,
    find_child_with_name_in_data,
    get_linked_record_id_with_name_in_data,
)


def transform_organisation(old_org: dict) -> ET.Element:
    old_org_data = old_org["record"]["data"]
    old_record_info = find_child_with_name_in_data(
        old_org_data["children"], "recordInfo"
    )
    assert old_record_info is not None

    organisation = create_group(
        "organisation",
        children=[
            create_group(
                "recordInfo",
                children=[
                    _create_validation_type(old_record_info),
                    _create_data_divider(),
                    _create_permission_unit(old_record_info),
                    _create_old_id(old_record_info),
                ],
            ),
            _create_genre_type_organisation_type(old_record_info),
            _create_name_swedish(old_org_data),
            _create_name_english(old_org_data),
            _create_end_date(old_org_data),
            _create_address(old_org_data),
            _create_local_id(old_org_data),
            _create_organisation_number(old_org_data),
            _create_location(old_org_data),
        ],
    )

    assert organisation is not None
    return organisation


def _create_validation_type(old_record_info: dict):
    old_record_type = get_linked_record_id_with_name_in_data(
        old_record_info["children"], "type"
    )

    return create_record_link(
        "validationType", "validationType", _transform_validation_type(old_record_type)
    )


def _create_data_divider():
    data_divider = create_record_link("dataDivider", "system", "divaData")
    return data_divider


def _create_permission_unit(old_record_info: dict):
    domain = get_first_atomic_value_with_name_in_data(
        old_record_info["children"], "domain"
    )
    assert domain is not None
    return create_record_link(
        "permissionUnit", "permissionUnit", domain_to_permission_unit(domain)
    )


def _create_old_id(old_record_info: dict):

    return create_text(
        "oldId",
        get_first_atomic_value_with_name_in_data(old_record_info["children"], "id"),
    )


def _create_genre_type_organisation_type(old_record_info: dict):

    old_record_type = get_linked_record_id_with_name_in_data(
        old_record_info["children"], "type"
    )

    return create_text(
        "genre",
        type="organisationType",
        value=_transform_organisation_type(old_record_type),
    )


def _create_name_swedish(old_org_data: dict):
    old_name_group = find_child_with_name_in_data(
        old_org_data["children"], "organisationName"
    )
    if old_name_group is None:
        return None

    old_name = get_first_atomic_value_with_name_in_data(
        old_name_group["children"], "name"
    )

    return create_group(
        "authority",
        lang="swe",
        repeatId="swe",
        children=[
            create_group(
                "name", type="corporate", children=[create_text("namePart", old_name)]
            )
        ],
    )


def _create_name_english(old_org_data: dict):
    old_name_group = find_child_with_name_in_data(
        old_org_data["children"], "organisationAlternativeName"
    )
    if old_name_group is None:
        return None

    old_name = get_first_atomic_value_with_name_in_data(
        old_name_group["children"], "name"
    )

    return create_group(
        "authority",
        lang="eng",
        repeatId="eng",
        children=[
            create_group(
                "name", type="corporate", children=[create_text("namePart", old_name)]
            )
        ],
    )


def _create_end_date(old_org_data: dict):
    closed_date = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "closedDate"
    )
    if closed_date is None:
        return None

    year, month, day = closed_date.split("-")

    return create_group(
        "endDate",
        children=[
            create_text("year", year),
            create_text("month", month),
            create_text("day", day),
        ],
    )


def _create_address(old_org_data: dict):
    old_address_group = find_child_with_name_in_data(
        old_org_data["children"], "address"
    )
    if old_address_group is None:
        return None
    box = get_first_atomic_value_with_name_in_data(old_address_group["children"], "box")
    street = get_first_atomic_value_with_name_in_data(
        old_address_group["children"], "street"
    )
    city = get_first_atomic_value_with_name_in_data(
        old_address_group["children"], "city"
    )
    postal_code = get_first_atomic_value_with_name_in_data(
        old_address_group["children"], "postcode"
    )
    country = get_first_atomic_value_with_name_in_data(
        old_address_group["children"], "country"
    )

    return create_group(
        "address",
        children=[
            create_text("postOfficeBox", box),
            create_text("street", street),
            create_text("postcode", postal_code),
            create_text("city", city),
            create_text("country", _transform_country(country)) if country is not None else None,
        ],
    )


def _create_local_id(old_org_data: dict):
    old_org_code = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "organisationCode"
    )
    return create_text("identifier", type="localId", value=old_org_code)


def _create_organisation_number(old_org_data: dict):
    old_org_number = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "organisationNumber"
    )
    return create_text("identifier", type="organisationNumber", value=old_org_number)


def _create_location(old_org_data: dict):
    old_location = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "URL"
    )

    return create_group(
        "location",
        children=[create_text("url", old_location)],
    )


def domain_to_permission_unit(domain: str) -> str:
    if domain == "esh":
        newDomain = "mchs"
        return newDomain
    elif domain == "mdh":
        newDomain = "mdu"
        return newDomain
    elif domain == "hj":
        newDomain = "ju"
        return newDomain
    elif domain == "uniarts":
        newDomain = "skh"
        return newDomain
    elif domain == "sprakochfolkminnen":
        newDomain = "isof"
        return newDomain
    elif domain == "ths":
        newDomain = "ehs"
        return newDomain
    else:
        return domain


def _transform_country(country):
    if country == "SE":
        return "sw"
    elif country == "FI":
        return "fi"
    elif country == "DK":
        return "dk"
    else:
        raise Exception(f"Unknown country code: {country}")


def _transform_validation_type(
    old_record_type,
):
    if old_record_type == "subOrganisation":
        return "diva-partOfOrganisation"
    elif old_record_type == "topOrganisation":
        return "diva-topOrganisation"
    else:
        raise Exception(f"Unknown validation type: {old_record_type}")


def _transform_organisation_type(
    old_record_type,
):
    if old_record_type == "subOrganisation":
        return "partOfOrganisation"
    elif old_record_type == "topOrganisation":
        return "topOrganisation"
    else:
        raise Exception(f"Unknown validation type: {old_record_type}")
