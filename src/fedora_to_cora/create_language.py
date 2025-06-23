import xml.etree.ElementTree as ET


def create_language(source_record: ET.Element) -> ET.Element:
    language_code = source_record.find(
        "./originalPublicationTitle/language/languageCode3"
    )

    assert (
        language_code is not None and language_code.text is not None
    ), "originalPublicationTitle/language/languageCode3 must be present in source_record"

    language = ET.Element("language", repeatId="0")
    languageTerm = ET.SubElement(language, "languageTerm")
    languageTerm.attrib["type"] = "code"
    languageTerm.attrib["authority"] = "iso639-2b"
    languageTerm.text = language_code.text

    return language
