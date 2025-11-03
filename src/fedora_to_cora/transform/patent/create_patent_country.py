import xml.etree.ElementTree as ET


def create_patent_country(source_record: ET.Element) -> ET.Element | None:
    country_source = source_record.findtext("./patentCountry/countryCode")

    if country_source is None:
        return None

    patent_country = ET.Element("patentCountry")
    patent_country.text = country_source

    return patent_country
