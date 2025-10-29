import xml.etree.ElementTree as ET


def create_language(source_record: ET.Element) -> ET.Element | None:
    language_code = source_record.find(
        "./originalPublicationTitle/language/languageCode3"
    )

    if language_code is None:
        return None

    language = ET.Element("language", repeatId="0")
    languageTerm = ET.SubElement(language, "languageTerm")
    languageTerm.attrib["type"] = "code"
    languageTerm.attrib["authority"] = "iso639-2b"
    languageTerm.text = language_code.text

    return language
