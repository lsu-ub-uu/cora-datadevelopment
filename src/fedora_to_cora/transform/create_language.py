import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_language(source_record: ET.Element) -> ET.Element | None:
    language_code = source_record.find(
        "./originalPublicationTitle/language/languageCode3"
    )

    if language_code is None:
        return None

    return create_group(
        "language",
        repeatId="0",
        children=[
            create_text(
                "languageTerm",
                type="code",
                authority="iso639-2b",
                value=language_code.text,
            )
        ],
    )
