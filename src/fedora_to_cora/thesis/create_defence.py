import xml.etree.ElementTree as ET


def create_defence(source_record: ET.Element) -> ET.Element:
    defence = ET.Element("defence")

    language = _create_language(source_record)
    defence.append(language)

    date_other = _create_duration(source_record)
    defence.append(date_other)

    location = _create_location(source_record)
    defence.append(location)

    address = _create_address(source_record)
    defence.append(address)

    place = _create_place(source_record)
    defence.append(place)

    return defence


def _create_place(source_record: ET.Element) -> ET.Element:
    place = ET.Element("place")
    city = source_record.findtext(
        "./defence/grantingInstitution/organisationAddress/city"
    )
    ET.SubElement(place, "placeTerm").text = city
    return place


def _create_address(source_record: ET.Element) -> ET.Element:
    address = ET.Element("address")
    street = source_record.findtext("./defence/room/street")
    post_number = source_record.findtext(
        "./defence/grantingInstitution/organisationAddress/postnumber"
    )
    city = source_record.findtext(
        "./defence/grantingInstitution/organisationAddress/city"
    )
    country = source_record.findtext(
        "./defence/grantingInstitution/organisationAddress/country/countryCode"
    )
    address.text = f"{street}, {post_number}, {city}, {country}"

    return address


def _create_location(source_record: ET.Element) -> ET.Element:
    location = ET.Element("location")
    room = source_record.findtext("./defence/room/name")
    location.text = room
    return location


def _create_language(source_record: ET.Element) -> ET.Element:
    language = ET.Element("language")
    lanugage_term = ET.Element("languageTerm", type="code", authority="iso639-2b")
    language_code_3 = source_record.findtext("./defence/language/languageCode3")
    assert language_code_3 is not None, "language must be present in source_record"
    lanugage_term.text = language_code_3
    language.append(lanugage_term)
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
