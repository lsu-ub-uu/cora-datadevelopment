import xml.etree.ElementTree as ET


def create_title_info(source_record: ET.Element) -> ET.Element:
    originalPublicationTitle = source_record.find(".//originalPublicationTitle")
    assert (
        originalPublicationTitle is not None
    ), "originalPublicationTitle must be present in source_record"
    return _create_title_info(originalPublicationTitle)


def create_title_info_type_alternative(
    source_record: ET.Element,
) -> list[ET.Element]:
    source_titles = source_record.findall(".//alternativePublicationTitles/title")

    return [
        _create_alternative_title(source_title, repeat_id)
        for repeat_id, source_title in enumerate(source_titles)
        if source_title is not None
    ]


def _create_alternative_title(source_title: ET.Element, repeat_id: int) -> ET.Element:
    title_info = _create_title_info(source_title)
    title_info.set("type", "alternative")
    title_info.set("repeatId", str(repeat_id))

    return title_info


def _create_title_info(source_title: ET.Element) -> ET.Element:
    languageCode, title = _validate(source_title)

    titleInfo = ET.Element("titleInfo", lang=languageCode)
    ET.SubElement(titleInfo, "title").text = title
    sub_title = source_title.find(".//subTitle")
    if sub_title is not None and sub_title.text:
        ET.SubElement(titleInfo, "subtitle").text = sub_title.text

    return titleInfo


def _validate(source_title: ET.Element):
    languageCode = source_title.find(".//language/languageCode3")
    title = source_title.find(".//title")
    assert (
        languageCode is not None and languageCode.text is not None
    ), "/language/languageCode3 must be present in title"
    assert (
        title is not None and title.text is not None
    ), "title must be present in title"

    return (languageCode.text, title.text)
