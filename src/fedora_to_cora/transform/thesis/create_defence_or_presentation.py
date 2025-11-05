import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


def create_defence_or_presentation(source_record: ET.Element) -> ET.Element:
    tag_name = "presentation" if _is_degree_project(source_record) else "defence"
    defence = ET.Element(tag_name)

    append_if_value(defence, _create_language(source_record))

    append_if_value(defence, _create_duration(source_record))

    append_if_value(defence, _create_location(source_record))

    append_if_value(defence, _create_address(source_record))

    append_if_value(defence, _create_place(source_record))

    return defence


def _is_degree_project(source_record: ET.Element) -> bool:
    return (
        get_validation_type_from_fedora_record(source_record) == "diva_degree-project"
    )


def _create_place(source_record: ET.Element) -> ET.Element:
    place = ET.Element("place")
    city = source_record.findtext("./defence/room/city")
    if city is not None:
        ET.SubElement(place, "placeTerm").text = city
    return place


def _create_address(source_record: ET.Element) -> ET.Element:
    address = ET.Element("address")
    street = source_record.findtext("./defence/room/street")
    address.text = street

    return address


def _create_location(source_record: ET.Element) -> ET.Element:
    location = ET.Element("location")
    room = source_record.findtext("./defence/room/name")
    location.text = room
    return location


def _create_language(source_record: ET.Element) -> ET.Element:
    language = ET.Element("language")
    language_term = ET.Element("languageTerm", type="code", authority="iso639-2b")
    language_code_3 = source_record.findtext("./defence/language/languageCode3")
    language_term.text = language_code_3

    append_if_value(language, language_term)
    return language


def _create_duration(source_record: ET.Element) -> ET.Element:
    duration_source = source_record.findtext("./defence/date")
    duration = ET.Element("dateOther", type="presentation")

    if duration_source is not None:
        date_part, time_part = duration_source.split("T")
        year, month, day = date_part.split("-")
        time_part = time_part.split("+")[0]  # Remove timezone offset
        hh, mm, _ = time_part.split(":")

        year_element = ET.SubElement(duration, "year")
        year_element.text = year

        month_element = ET.SubElement(duration, "month")
        month_element.text = month

        day_element = ET.SubElement(duration, "day")
        day_element.text = day

        hh_element = ET.SubElement(duration, "hh")
        hh_element.text = hh

        mm_element = ET.SubElement(duration, "mm")
        mm_element.text = mm

    return duration
