from cora.context import Context
from xml.etree import ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from cora.cora_json_utils import (
    get_first_atomic_value_with_name_in_data,
    find_child_with_name_in_data,
    get_linked_record_id_with_name_in_data,
)


def transform_organisation(old_org: dict, context: Context) -> ET.Element:
    # Placeholder for transformation logic
    organisation = ET.Element(
        "organisation"
    )  # Replace with actual transformed XML element
    old_org_data = old_org["record"]["data"]
    old_record_info = find_child_with_name_in_data(
        old_org_data["children"], "recordInfo"
    )
    record_info = ET.SubElement(organisation, "recordInfo")
    record_info.append(_create_validation_type(old_record_info))
    record_info.append(_create_data_divider())
    record_info.append(_create_permission_unit(old_record_info))
    record_info.append(_create_old_id(old_record_info))

    organisation.append(_create_genre_type_organisation_type(old_record_info))
    append_if_value(organisation, _create_name_swedish(old_org_data))
    append_if_value(organisation, _create_name_english(old_org_data))
    append_if_value(organisation, _create_end_date(old_org_data))
    append_if_value(organisation, _create_address(old_org_data))
    append_if_value(organisation, _create_organisation_code(old_org_data))
    append_if_value(organisation, _create_organisation_number(old_org_data))
    append_if_value(organisation, _create_location(old_org_data))
    return organisation


def _create_validation_type(old_record_info: dict):
    old_record_type = get_linked_record_id_with_name_in_data(
        old_record_info["children"], "type"
    )

    return create_record_link_using_name_type_id(
        "validationType", "validationType", _transform_validation_type(old_record_type)
    )


def _create_data_divider():
    data_divider = create_record_link_using_name_type_id(
        "dataDivider", "system", "divaData"
    )
    return data_divider


def _create_permission_unit(old_record_info: dict):
    domain = get_first_atomic_value_with_name_in_data(
        old_record_info["children"], "domain"
    )
    return create_record_link_using_name_type_id(
        "permissionUnit", "permissionUnit", domain_to_permission_unit(domain)
    )


def _create_old_id(old_record_info: dict):
    old_id = get_first_atomic_value_with_name_in_data(old_record_info["children"], "id")
    old_id_element = ET.Element("oldId")
    old_id_element.text = old_id
    return old_id_element


def _create_genre_type_organisation_type(old_record_info: dict):
    old_record_type = get_linked_record_id_with_name_in_data(
        old_record_info["children"], "type"
    )

    genre = ET.Element("genre", type="organisationType")
    genre.text = _transform_organisation_type(old_record_type)
    return genre


def _create_name_swedish(old_org_data: dict):
    old_name_group = find_child_with_name_in_data(
        old_org_data["children"], "organisationName"
    )
    if old_name_group is None:
        return None

    old_name = get_first_atomic_value_with_name_in_data(
        old_name_group["children"], "name"
    )

    authority = ET.Element("authority", lang="swe")
    name = ET.SubElement(authority, "name", type="corporate")
    name_part = ET.SubElement(name, "namePart")

    name_part.text = old_name
    return authority


def _create_name_english(old_org_data: dict):
    old_name_group = find_child_with_name_in_data(
        old_org_data["children"], "organisationAlternativeName"
    )
    if old_name_group is None:
        return None

    old_name = get_first_atomic_value_with_name_in_data(
        old_name_group["children"], "name"
    )

    authority = ET.Element("variant", lang="eng")
    name = ET.SubElement(authority, "name", type="corporate")
    name_part = ET.SubElement(name, "namePart")

    name_part.text = old_name
    return authority


def _create_end_date(old_org_data: dict):
    closed_date = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "closedDate"
    )
    if closed_date is None:
        return None

    year, month, day = closed_date.split("-")
    end_date_element = ET.Element("endDate")
    ET.SubElement(end_date_element, "year").text = year
    ET.SubElement(end_date_element, "month").text = month
    ET.SubElement(end_date_element, "day").text = day
    return end_date_element


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

    address_element = ET.Element("address")
    if box:
        ET.SubElement(address_element, "postOfficeBox").text = box
    if street:
        ET.SubElement(address_element, "street").text = street
    if postal_code:
        ET.SubElement(address_element, "postcode").text = postal_code
    if city:
        ET.SubElement(address_element, "place").text = city
    if country:
        ET.SubElement(address_element, "country").text = _transform_country(country)

    return address_element


def _create_organisation_code(old_org_data: dict):
    old_org_code = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "organisationCode"
    )
    if old_org_code is None:
        return None

    organisation_code_element = ET.Element("identifier", type="organisationCode")
    organisation_code_element.text = old_org_code
    return organisation_code_element


def _create_organisation_number(old_org_data: dict):
    old_org_number = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "organisationNumber"
    )
    if old_org_number is None:
        return None

    organisation_number_element = ET.Element("identifier", type="organisationNumber")
    organisation_number_element.text = old_org_number
    return organisation_number_element


def _create_location(old_org_data: dict):
    old_location = get_first_atomic_value_with_name_in_data(
        old_org_data["children"], "URL"
    )
    if old_location is None:
        return None

    location_element = ET.Element("location")
    url = ET.SubElement(location_element, "url")
    url.text = old_location
    return location_element


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
