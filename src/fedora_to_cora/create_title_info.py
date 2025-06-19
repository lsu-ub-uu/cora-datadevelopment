import xml.etree.ElementTree as ET


def create_title_info(source_record: ET.Element) -> ET.Element:
    languageCode, title = _validate(source_record)

    titleInfo = ET.Element("titleInfo", lang=languageCode)
    ET.SubElement(titleInfo, "title").text = title
    sub_title = source_record.find(".//subTitle")
    if sub_title is not None and sub_title.text:
        ET.SubElement(titleInfo, "subTitle").text = sub_title.text

    return titleInfo


def _validate(source_record: ET.Element):
    languageCode = source_record.find(
        "./originalPublicationTitle/language/languageCode3"
    )
    title = source_record.find(".//title")
    assert (
        languageCode is not None and languageCode.text is not None
    ), "originalPublicationTitle/language/languageCode3 must be present in source_record"
    assert (
        title is not None and title.text is not None
    ), "title must be present in source_record"

    return (languageCode.text, title.text)
