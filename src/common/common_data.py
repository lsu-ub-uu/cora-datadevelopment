import xml.etree.ElementTree as ET
from common.create_end_date import append_year_month_day


def read_source_xml(filePath_sourceXml) -> ET.Element:
    sourceFile_xml = ET.parse(filePath_sourceXml)
    root = sourceFile_xml.getroot()
    
    return root


def create_title_info(title: str, subtitle: str) -> ET.Element:
    title_info = ET.Element("titleInfo")
    title_info.append(
        create_element_from_source("title", value = title)
        )
    if subtitle is not None and subtitle.text:
        title_info.append(
            create_element_from_source("subtitle", value = subtitle.text)
            )
    return title_info


def create_identifiers_from_source_with_repeat_id(identifier: str, identifier_type: str, identifier_repeat_id: dict) -> ET.Element:
    identifier_element = create_identifiers_from_source(identifier, identifier_type)
    identifier_element.set("displayLabel", identifier_type)
    identifier_element.set("repeatId", str(identifier_repeat_id["repeatId"]))
    identifier_repeat_id["repeatId"] = identifier_repeat_id["repeatId"] + 1
    identifier_element.set("type", "issn")
    return identifier_element
    
def create_identifiers_from_source(identifier: str, identifier_type: str) -> ET.Element:
    identifiers = ET.Element("identifier", type = identifier_type)
    identifiers.text = identifier
    
    return identifiers




def create_origin_info(date: str, origin_type: str):
    origin_info = ET.Element(origin_type)
    date_issued = ET.Element("dateIssued", point="end")
    
    year, month, day = map(str.strip, date.split("-"))
    append_year_month_day(date_issued, year, month, day)
    
    origin_info.append(date_issued)
    
    return origin_info

def create_location(url:str) -> ET.Element:
    location = ET.Element("location")
    location.append(
        create_element_from_source("url", value = url)
        )
    return location


def create_record_link_using_name_type_id(
    name_in_data: str, record_type: str, record_id: str) -> ET.Element:
    link = ET.Element(name_in_data)
    ET.SubElement(link, "linkedRecordType").text = record_type
    ET.SubElement(link, "linkedRecordId").text = record_id
    return link


def create_element_from_source(tag_name: str, value: str) -> ET.Element:
    element = ET.Element(tag_name)
    element.text = value
    
    return element







def remove_action_link(element):
    for actionLinks in element.findall("actionLinks"):
        element.remove(actionLinks)


def remove_actionLinks_from_record(record, name_in_data):
    for clean_record in record.findall(f".//{name_in_data}"):
        for validationType in clean_record.findall(".//validationType"):
            remove_action_link(validationType)
        for dataDivider in clean_record.findall(".//dataDivider"):
            remove_action_link(dataDivider)
        for permissionUnit in clean_record.findall(".//permissionUnit"):
            remove_action_link(permissionUnit)
        for type in clean_record.findall(".//type"):
            remove_action_link(type)
        for createdBy in clean_record.findall(".//createdBy"):
            remove_action_link(createdBy)
        for updatedBy in clean_record.findall(".//updatedBy"):
            remove_action_link(updatedBy)
    return clean_record


def validateRecord_build(record_type, filePath_validateBase, newRecordToCreate):
    validationOrder_root = read_source_xml(filePath_validateBase)
    validationOrder_root.find(".//recordType/linkedRecordId").text = record_type
    validationOrder_root.find(".//validateLinks").text = "false"
    validationOrder_root.find(".//metadataToValidate").text = "new"
    record = validationOrder_root.find(".//record")
    record.append(newRecordToCreate)
    return validationOrder_root


def record_info_build(recordType, permission_unit, data_record, newRecordElement):
    recordInfo = ET.SubElement(newRecordElement, "recordInfo")
    validationType = ET.SubElement(recordInfo, "validationType")
    ET.SubElement(validationType, "linkedRecordType").text = "validationType"
    ET.SubElement(validationType, "linkedRecordId").text = "diva-" + recordType
    dataDivider = ET.SubElement(recordInfo, "dataDivider")
    ET.SubElement(dataDivider, "linkedRecordType").text = "system"
    ET.SubElement(dataDivider, "linkedRecordId").text = "divaData"
    if permission_unit is not None:
        permissionUnit = ET.SubElement(recordInfo, "permissionUnit")
        ET.SubElement(permissionUnit, "linkedRecordType").text = "permissionUnit"
        ET.SubElement(permissionUnit, "linkedRecordId").text = permission_unit
    oldId_fromSource = data_record.find(".//old_id")
    if oldId_fromSource is not None and oldId_fromSource.text:
        ET.SubElement(recordInfo, "oldId").text = oldId_fromSource.text


def get_oldId(data_record):
    oldId_fromSource = data_record.find(".//old_id")
    # print(oldId_fromSource.text)
    return oldId_fromSource.text


def name_build(data_record, new_record_element):
    name_fromSource = data_record.find(".//name")
    if name_fromSource is not None and name_fromSource.text:
        name = ET.SubElement(new_record_element, "name", type="corporate")
        ET.SubElement(name, "namePart").text = name_fromSource.text


def nameAuthorityVariant_build(data_record, newRecordElement, elementName, language):
    nameLang_fromSource = data_record.find(f".//name_{language}")
    if nameLang_fromSource is not None and nameLang_fromSource.text:
        name = ET.SubElement(newRecordElement, elementName, lang=language)
        nameType = ET.SubElement(name, "name", type="corporate")
        ET.SubElement(nameType, "namePart").text = nameLang_fromSource.text



def topicAuthorityVariant_build(data_record, newRecordElement, elementName, language):
    topicLang_fromSource = data_record.find(f".//topic_{language}")
    topic = ET.SubElement(newRecordElement, elementName, lang=language)
    ET.SubElement(topic, "topic").text = topicLang_fromSource.text


def title_info_build(data_record, newRecordElement):
    title_fromSource = data_record.find(f".//title")
    if title_fromSource is not None and title_fromSource.text:
        titleInfo = ET.SubElement(newRecordElement, "titleInfo")
        ET.SubElement(titleInfo, "title").text = title_fromSource.text
    subTitle_fromSource = data_record.find(f".//subTitle")
    if subTitle_fromSource is not None and subTitle_fromSource.text:
        ET.SubElement(titleInfo, "subTitle").text = subTitle_fromSource.text


def titleInfo_alternative_build(data_record, new_record_element, titleType):
    title_from_source = data_record.find(".//alternative_title")
    if title_from_source is not None and title_from_source.text:
        titleInfo = ET.SubElement(new_record_element, "titleInfo", type=titleType)
        ET.SubElement(titleInfo, "title").text = title_from_source.text
    subTitleFromSource = data_record.find(".//alternative_sub_title")
    if subTitleFromSource is not None and subTitleFromSource.text:
        ET.SubElement(titleInfo, "subTitle").text = subTitleFromSource.text



def identifier_build(data_record, newRecordElement, identifierType, counter):
    identifier_fromSource = data_record.find(f".//identifier_{identifierType}")
    if identifier_fromSource is not None and identifier_fromSource.text:
        if identifierType in ("pissn", "eissn"):
            ET.SubElement(
                newRecordElement, "identifier", displayLabel=identifierType, type="issn"
            ).text = identifier_fromSource.text
        #                ET.SubElement(newRecordElement, 'identifier', displayLabel=identifierType, repeatId=str(counter), type = 'issn').text = identifier_fromSource.text
        #                counter += 1
        else:
            ET.SubElement(newRecordElement, "identifier", type=identifierType).text = (
                identifier_fromSource.text
            )
    return counter



def end_date_build(data_record, newRecordElement, originType):
    date_fromSource = data_record.find(".//end_date")
    if date_fromSource is not None and date_fromSource.text:
        year, month, day = map(str.strip, date_fromSource.text.split("-"))
        if originType == "originInfo":
            originInfo = ET.SubElement(newRecordElement, originType)
            dateIssued = ET.SubElement(originInfo, "dateIssued", point="end")
            endDate_yearMonthDay(year, month, day, dateIssued)
        elif originType == "organisationInfo":
            organisationInfo = ET.SubElement(newRecordElement, originType)
            endDate = ET.SubElement(organisationInfo, "endDate")
            endDate_yearMonthDay(year, month, day, organisationInfo)
        else:
            endDate = ET.SubElement(newRecordElement, "endDate")
            endDate_yearMonthDay(year, month, day, endDate)


def endDate_yearMonthDay(year: str, month: str, day: str, rootElement: ET.Element):
    ET.SubElement(rootElement, "year").text = year
    ET.SubElement(rootElement, "month").text = month
    ET.SubElement(rootElement, "day").text = day
    
    
    
def location_build(data_record, newRecordElement):
    url_fromSource = data_record.find(".//url")
    if url_fromSource is not None and url_fromSource.text:
        location = ET.SubElement(newRecordElement, "location")
        ET.SubElement(location, "url").text = url_fromSource.text


def note_build(data_record, newRecordElement, noteType):
    note_fromSource = data_record.find(f".//note_{noteType}")
    if note_fromSource is not None and note_fromSource.text:
        ET.SubElement(newRecordElement, "note", type="external").text = (
            note_fromSource.text
        )


def genre_build(data_record, new_record_element, publication_map, counter):
    genre_from_source = data_record.find(".//publication_type_id")
    if genre_from_source is not None and genre_from_source.text:
        genre_value = publication_map[genre_from_source.text]
        ET.SubElement(
            new_record_element, "genre", repeatId=str(counter), type="outputType"
        ).text = genre_value
        counter += 1
    return counter


def create_record_info_for_record_type(record_type: str) -> ET.Element:
    record_info = ET.Element("recordInfo")

    validation_type = create_record_link_using_name_type_id(
        "validationType", "validationType", "diva-" + record_type
    )
    record_info.append(validation_type)

    data_divider = create_record_link_using_name_type_id(
        "dataDivider", "system", "divaData"
    )
    record_info.append(data_divider)

    #        oldId_fromSource = data_record.find('.//old_id')
    #        ET.SubElement(recordInfo, 'oldId').text = oldId_fromSource.text
    return record_info



