import xml.etree.ElementTree as ET
from common.xml_utils import create_text, create_group
from fedora_to_cora.clean_rich_text import clean_rich_text


def create_title_info(source_record: ET.Element) -> ET.Element | None:
    originalPublicationTitle = source_record.find("./originalPublicationTitle")

    if originalPublicationTitle is None:
        return None

    return _create_title_info(originalPublicationTitle)


def create_title_info_type_alternative(
    source_record: ET.Element,
) -> list[ET.Element]:
    source_titles = source_record.findall("./alternativePublicationTitles/title")

    title_infos = [
        _create_alternative_title(source_title, repeat_id)
        for repeat_id, source_title in enumerate(source_titles)
        if source_title is not None
    ]

    return [title_info for title_info in title_infos if title_info is not None]


def _create_alternative_title(
    source_title: ET.Element, repeat_id: int
) -> ET.Element | None:
    title_info = _create_title_info(source_title)
    if title_info is None:
        return None

    title_info.set("type", "alternative")
    title_info.set("repeatId", str(repeat_id))

    return title_info


def _create_title_info(source_title: ET.Element) -> ET.Element | None:
    language_code = source_title.findtext("./language/languageCode3")

    if language_code is None:
        return None

    return create_group(
        "titleInfo",
        lang=language_code,
        children=[
            create_text("title", clean_rich_text(source_title.findtext("./title"))),
            create_text(
                "subtitle", clean_rich_text(source_title.findtext("./subTitle"))
            ),
        ],
    )
