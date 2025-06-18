import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id, read_source_xml
from fedora_to_cora.get_validation_type_by_publication_type_id import get_validation_type_by_publication_type_id
from fedora_to_cora.get_visibility import get_visibility
from fedora_to_cora.get_content_type import get_content_type


def create_record_info(source_record):
    recordInfo = ET.Element("recordInfo")


    ET.SubElement(recordInfo, "validationType").text = get_validation_type_by_publication_type_id(
        source_record.find(".//publicationTypeId").text
    )

    ET.SubElement(recordInfo, "dataDivider").text = "divaData"

    recordInfo.append(create_record_link_using_name_type_id(
        "permissionUnit",
        "permissionUnit",
        source_record.find(".//domain").text
    ))

    ET.SubElement(recordInfo, "visibility").text = get_visibility(source_record)


    pid = source_record.find(".//pid")
    if pid is not None and pid.text:
        ET.SubElement(recordInfo, "oldId").text = pid.text

    return recordInfo

def create_variable(source_record, old_name, new_name, attributes, transform_value=None):
    variable = ET.Element(new_name)
    old_variable = source_record.find(f".//{old_name}")
    value = old_variable.text if old_variable is not None else None
    old_content = transform_value(value) if callable(transform_value) else value

    if attributes is not None and attributes:
        variable = ET.Element(new_name, attrib=attributes)
        variable.text = str(old_content)
    else:
        variable = ET.Element(new_name)
        variable.text = str(old_content)

    return variable

def create_title(source_record):
    attributes = {"lang": source_record.find("./originalPublicationTitle/language/languageCode3").text}
    titleInfo = ET.Element('titleInfo', attrib=attributes)
    ET.SubElement(titleInfo, 'title').text = source_record.find(".//title").text
    sub_title = source_record.find(".//subTitle")
    if sub_title is not None and sub_title.text:
        ET.SubElement(titleInfo, "subTitle").text = sub_title.text

    return titleInfo

def create_subject(source_record):
    attributes = {"lang": source_record.find("./keyWords/entry/language/languageCode3").text}
    subject = ET.Element("subject", attrib=attributes)
    ET.SubElement(subject, 'topic').text = source_record.find("./keyWords/entry/list/string").text

    return subject

def transform_to_cora_output(filename):
    print(filename)
    source_record = read_source_xml(filename)
    target_record = ET.Element("output")

    target_record.append(create_record_info(source_record))
    target_record.append(create_variable(source_record, "contentTypeCode", "genre", {"type":"contentType"}, get_content_type ))
    target_record.append(create_title(source_record))
    target_record.append(create_subject(source_record))

    return target_record
   


