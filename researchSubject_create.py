from multiprocessing import Pool
import time
import requests
import xml.etree.ElementTree as ET
from collections import OrderedDict 
from secretdata import SecretData

# hämta en xml-fil per domän via sql-script (separat)
# kör detta pythonscript, en domän i taget.


# basic url for records
base_url = {
    'preview': 'https://cora.epc.ub.uu.se/diva/rest/record/',
    'dev': 'http://130.238.171.238:38082/diva/rest/record/',
    'pre': 'https://pre.diva-portal.org/rest/record/',
    'mig': 'https://mig.diva-portal.org/rest/record/'
}

# url for get authToken
token_url = {
    'preview': 'https://cora.epc.ub.uu.se/diva/',
    'pre': 'https://pre.diva-portal.org/',
    'mig': 'https://mig.diva-portal.org/'
}

# endpoints for url
endpoint = {
    'diva-subject': 'diva-subject',
    'diva-subject_search': 'searchResult/diva-subjectSearch?',
    'token_end': 'login/rest/apptoken'
}

system = 'preview'
recordType = 'diva-subject'
recordContentSource = 'polar' # <-- ändra till rätt domän
#validateLinks = 'true'
#validateMetadata = 'new'
WORKERS = 16

# filer
filePath_validateBase = (r'validationOrder_base.xml')
filePath_source_xml = (r"db_xml\researchSubject_"+recordContentSource+"_db.xml")

# listor
relationOldNewIds = OrderedDict()
linksToEarlierId = OrderedDict()  
linksToBroaderId = OrderedDict()

def start():
    dataList = read_source_xml(filePath_source_xml) 
    authToken = SecretData.get_authToken(system)
    starttime = time.time()
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        list_dataRecord.append(data_record)
        #preview_parse_record(data_record) # <-- förhandsgranska record
        #preview_validate_record(data_record) # <-- förhandsgranska workorder
        #validate_record(data_record) # <-- gör en requests
        created_CoraRecord = create_new_record(data_record) # <-- gör en requests
        relationOldNewIds, linksToEarlierId, linksToBroaderId = store_migrationData(created_CoraRecord, data_record)
        
        """    if __name__ == "__main__":
        with Pool(WORKERS) as pool:
            pool.map(validate_record, list_dataRecord)""" #<-- gör en requests
        
    loop_earlier(authToken, relationOldNewIds, linksToEarlierId) # <-- gör en update baserat på id i listan
    loop_broader(authToken, relationOldNewIds, linksToBroaderId) # <-- gör en update baserat på id i listan
    
    print(f'Tidsåtgång: {time.time() - starttime}')

# BEHÖVER EV. VÄNDA OCH UTGÅ FRÅN UPDATE ISTÄLLET FÖR LISTAN?
# problemet nu är att jag behöver created_coraRecord... samt looparna, så vart lägger jag pool?

###################

# read source-file
def read_source_xml(filePath_source_xml):
    sourceFile_xml = ET.parse(filePath_source_xml)
    dataList = sourceFile_xml.getroot()
    return dataList

# parse and build record for new subject
def parse_new_subject_record(data_record):
        diva_subject = ET.Element('subject')
        recordInfo_build(recordType, recordContentSource, data_record, diva_subject)
        topic_build(data_record, diva_subject, 'authority', 'swe')
        topic_build(data_record, diva_subject, 'variant', 'eng')
        endDate_build(data_record, diva_subject)
        return diva_subject

# build recordInfo
def recordInfo_build(recordType, recordContentSource, data_record, diva_subject):
    recordInfo = ET.SubElement(diva_subject, 'recordInfo')
    ET.SubElement(recordInfo, 'recordContentSource').text = recordContentSource # <!-- ange source for record -->
    validationType = ET.SubElement(recordInfo, 'validationType')
    ET.SubElement(validationType, 'linkedRecordType').text = 'validationType'
    ET.SubElement(validationType, 'linkedRecordId').text = recordType # <!-- ange posttyp -->
    dataDivider = ET.SubElement(recordInfo, 'dataDivider')
    ET.SubElement(dataDivider, 'linkedRecordType').text = 'system'
    ET.SubElement(dataDivider, 'linkedRecordId').text = 'divaData' # <-- diva för metadata || divaData för records -->
    oldId_fromSource = data_record.find('.//old_id')
    ET.SubElement(recordInfo, 'oldId').text = oldId_fromSource.text

# build authority and variant topic name
def topic_build(data_record, diva_subject, elementName, language):
    topic_name_fromSource = data_record.find(f'.//topic_{language}')
    subject_topic = ET.SubElement(diva_subject, elementName, lang = language)
    ET.SubElement(subject_topic, 'topic').text = topic_name_fromSource.text

# build endDate if not empty value
def endDate_build(data_record, diva_subject):
    date_fromSource = data_record.find('.//end_date')
    if date_fromSource is not None and date_fromSource.text:
        year, month, day = map(str.strip, date_fromSource.text.split('-'))
        endDate = ET.SubElement(diva_subject, 'endDate')
        ET.SubElement(endDate, 'year').text = year
        ET.SubElement(endDate, 'month').text = month
        ET.SubElement(endDate, 'day').text = day

# preview new record base
def preview_parse_record(data_record):
    new_subject_record = parse_new_subject_record(data_record) # skapar själva posten i ny-läge
    print(ET.tostring(new_subject_record, encoding='UTF-8'))

# build validate record
def validate_subject_record_build(recordType, filePath_validateBase, new_subject_record_toCreate):
    validationOrder_baseFile = ET.parse(filePath_validateBase)
    validationOrder_root = validationOrder_baseFile.getroot()
    validationOrder_root.find('.//recordType/linkedRecordId').text = recordType # <!-- ange posttyp att validera -->
    validationOrder_root.find('.//validateLinks').text = 'false' # <!-- ange true/false för vaildering av länkar -->
    validationOrder_root.find('.//metadataToValidate').text = 'new' # <!-- ange new/existing för vaildering av metadata -->
    record = validationOrder_root.find('.//record')
    record.append(new_subject_record_toCreate)
    return validationOrder_root

# preview validate record
def preview_validate_record(data_record):
    new_subject_record_toCreate = parse_new_subject_record(data_record)
    subject_record_toValidate = validate_subject_record_build(recordType, filePath_validateBase, new_subject_record_toCreate)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(subject_record_toValidate).decode("UTF-8")
    print(output)

###################

# parse record for validate requests
def parse_validate_record(data_record):
    record_toCreate = parse_new_subject_record(data_record)
    record_toValidate = validate_subject_record_build(recordType, filePath_validateBase, record_toCreate)
    return record_toValidate

# validate record
def validate_record(data_record):
    authToken = SecretData.get_authToken(system)
    validate_headers_xml = {'Content-Type':'application/vnd.uub.workorder+xml', 'Accept':'application/vnd.uub.record+xml','authToken':authToken}
    validate_url = 'https://cora.epc.ub.uu.se/diva/rest/record/workOrder'
    record_toValidate = parse_validate_record(data_record)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(record_toValidate).decode("UTF-8")
    response = requests.post(validate_url, data=output, headers = validate_headers_xml)
    print(response.status_code, response.text)
    if '<valid>true</valid>' not in response.text:
        with open(f'researchSubject/response.xml', 'a', encoding='utf-8') as log:
            log.write(f"{response.status_code}. {response.text}\n\n")

# parse record for create requests
def parse_record(data_record):
    record_toCreate = parse_new_subject_record(data_record)
    return record_toCreate

# create record
def create_new_record(data_record):
    authToken = SecretData.get_authToken(system)
    headers_xml = {'Content-Type':'application/vnd.uub.record+xml', 'Accept':'application/vnd.uub.record+xml', 'authToken':authToken}
    create_url = base_url[system]+endpoint[recordType] # <-- anger miljö genom lista/val base_url -->
    record_toCreate = parse_record(data_record)
    
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(record_toCreate).decode("UTF-8")
    response = requests.post(create_url, data=output, headers = headers_xml)
    print(response.status_code)
    if response.status_code not in (200, 201, 409):
        with open('log.txt', 'a', encoding='utf-8') as log:
            log.write(f'{response.status_code}. {response.text}\n\n')
    return response.text

###################

# keep data from source at create, to use in update
def store_migrationData(created_CoraRecord, data_record):
    created_records = ET.fromstring(created_CoraRecord)
    created_records.findall('.//recordInfo')
    created_id = created_records.find('.//recordInfo/id')
    created_oldId = created_records.find('.//recordInfo/oldId')
    relationOldNewIds[created_oldId.text] = created_id.text
    earlier_ids = data_record.find('.//earlier_id')
    linksToEarlierId[created_id.text] = earlier_ids.text
    broader_ids = data_record.find('.//broader_id')
    linksToBroaderId[created_id.text] = broader_ids.text
    return relationOldNewIds, linksToEarlierId, linksToBroaderId

# build related part for link to related record
def related_subject_build(recordType, record_from_search_cleanRecord, relatedType, counter, value): 
    related = ET.SubElement(record_from_search_cleanRecord, 'related', repeatId=str(counter), type = relatedType)
    related_topic = ET.SubElement(related, 'topic')
    ET.SubElement(related_topic, 'linkedRecordType').text = recordType
    ET.SubElement(related_topic, 'linkedRecordId').text = value

# build link to related record if not empty value, handles multiple value for related type erlier
def related_subjectLinkedRecord_build(recordType, relationOldNewIds, earlierValue, record_from_search_cleanRecord, relatedType, counter):
    related_subject_id = map(str.strip, earlierValue.split(','))
    for relatedType_id_value in related_subject_id:
        for key, value in relationOldNewIds.items():
            if relatedType_id_value == key:
                related_subject_build(recordType, record_from_search_cleanRecord, relatedType, counter, value)
                counter += 1
    return counter

# går igenom listan med id, hämtar ut och städar posten samt skapar länk
def loop_earlier(authToken, relationOldNewIds, linksToEarlierId):
    for earlierKey, earlierValue in linksToEarlierId.items():
        if earlierValue is not None:
            record_from_search = search_query(authToken, earlierKey)
            dataList = ET.fromstring(record_from_search)
            updateUrl = dataList.find('.//actionLinks/update/url')
            record_from_search_cleanRecord = remove_actionLinks_from_record(dataList)
            counter = 0
            counter = related_subjectLinkedRecord_build(recordType, relationOldNewIds, earlierValue, record_from_search_cleanRecord, 'earlier', counter)
            update_new_record(record_from_search_cleanRecord, updateUrl)

# går igenom listan med id, hämtar ut och städar posten samt skapar länk
def loop_broader(authToken, relationOldNewIds, linksToBroaderId):
    for broaderKey, broaderValue in linksToBroaderId.items():
        if broaderValue is not None:
            print(f"broaderValue: {broaderValue}")
            print(f"broaderKey: {broaderKey}")
            record_from_search = search_query(authToken, broaderKey)
            print(record_from_search)
            dataList = ET.fromstring(record_from_search)
            updateUrl = dataList.find('.//actionLinks/update/url')
            print(F"url: {updateUrl.text}")
            record_from_search_cleanRecord = remove_actionLinks_from_record(dataList)
            counter = 10
            counter = related_subjectLinkedRecord_build(recordType, relationOldNewIds, broaderValue, record_from_search_cleanRecord, 'broader', counter)
            update_new_record(record_from_search_cleanRecord, updateUrl)

# update created record from search
def update_new_record(record_from_search_cleanRecord, updateUrl):
    authToken = SecretData.get_authToken(system)
    headers_xml = {'Content-Type':'application/vnd.uub.record+xml', 'Accept':'application/vnd.uub.record+xml', 'authToken':authToken}
    create_url = updateUrl.text
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(record_from_search_cleanRecord).decode("UTF-8")
    response = requests.post(create_url, data=output, headers = headers_xml)
    print(response.status_code, response.text)
    if response.status_code not in (200, 201, 409):
        with open('log.txt', 'a', encoding='utf-8') as log:
            log.write(f'{response.status_code}. {response.text}\n\n')
    return response.status_code, response.text
     
###################

# sök utifrån angivna sökparametrar
def search_query(authToken, created_recordId):
    search_url, search_headers_xml = search_parameters(authToken, created_recordId)
    response = requests.get(search_url, headers=search_headers_xml)
    return(response.text)

# definerar sökpratametrar
def search_parameters(authToken, created_recordId):
    recordId_search_query = 'searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"recordIdSearchTerm","value":"'+created_recordId+'"}]}]}]}'
    search_url = base_url[system]+endpoint['diva-subject_search']+recordId_search_query
    search_headers_xml = {'Accept':'application/vnd.uub.recordList+xml','authToken':authToken}
    return search_url, search_headers_xml

# ta bort alla actionLinks från recordInfo
def remove_actionLinks_from_record(subject):
    for clean_record in subject.findall('.//subject'):
        for validationType in clean_record.findall('.//validationType'):
            removeActionLink(validationType)
        for dataDivider in clean_record.findall('.//dataDivider'):
            removeActionLink(dataDivider)
        for type in clean_record.findall('.//type'):
            removeActionLink(type)
        for createdBy in clean_record.findall('.//createdBy'):
            removeActionLink(createdBy)
        for updatedBy in clean_record.findall('.//updatedBy'):
            removeActionLink(updatedBy)
    return clean_record

# ta bort alla actionLinks
def removeActionLink(element):
    for actionLinks in element.findall('actionLinks'):
        element.remove(actionLinks)


start()