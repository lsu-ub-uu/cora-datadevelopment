from multiprocessing import Pool
import time
import requests
import xml.etree.ElementTree as ET
from collections import OrderedDict 
from commondata import CommonData
from constantsdata import ConstantsData
from secretdata import SecretData

unit = 'polar'
system = 'preview'
recordType = 'subject'
WORKERS = 16
filePath_validateBase = (r"validationOrder_base.xml")
filePath_sourceXml = (r"db_xml\researchSubject_"+unit+"_db.xml")

def start():
    starttime = time.time()
    dataList = CommonData.read_source_xml(filePath_sourceXml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        list_dataRecord.append(data_record)
        # createdCoraRecord = create_record(data_record)
        # relationOldNewIds, linksToEarlierIds, linksToBroaderIds = store_ids(data_record, createdCoraRecord)

        # print(f"relation: {relationOldNewIds}")
        # print(f"pre: {linksToEarlierIds}")
        # print(f"host: {linksToBroaderIds}")

    # loop_id_lists(relationOldNewIds, linksToEarlierIds, linksToBroaderIds)

    if __name__ == "__main__":
        with Pool(WORKERS) as pool:
            pool.map(validate_record, list_dataRecord)

    print(f'Tidsåtgång: {time.time() - starttime}')


def new_record_build(data_record):
        newRecordElement = ET.Element(recordType)
        CommonData.recordInfoUnit_build(recordType, unit, data_record, newRecordElement)
        CommonData.topicAuthorityVariant_build(data_record, newRecordElement, 'authority', 'swe')
        CommonData.topicAuthorityVariant_build(data_record, newRecordElement, 'variant', 'eng')
        CommonData.endDate_build(data_record, newRecordElement, None)
        return newRecordElement

def validate_record(data_record):
    authToken = SecretData.get_authToken(system)
    validate_headers_xml = {'Content-Type':'application/vnd.uub.workorder+xml', 'Accept':'application/vnd.uub.record+xml','authToken':authToken}
    validate_url = 'https://cora.epc.ub.uu.se/diva/rest/record/workOrder'
    newRecordToCreate = new_record_build(data_record)
    newRecordToValidate = CommonData.validateRecord_build(recordType, filePath_validateBase, newRecordToCreate)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(newRecordToValidate).decode("UTF-8")
    response = requests.post(validate_url, data=output, headers = validate_headers_xml)
    print(response.status_code, response.text)
    if '<valid>true</valid>' not in response.text:
        with open(f'errorlog.txt', 'a', encoding='utf-8') as log:
            log.write(f"{response.status_code}. {response.text}\n\n")

def create_record(data_record):
    authToken = SecretData.get_authToken(system)
    headersXml = {'Content-Type':'application/vnd.uub.record+xml', 'Accept':'application/vnd.uub.record+xml', 'authToken':authToken}
    urlCreate = ConstantsData.BASE_URL[system]+"diva-"+recordType
    recordToCreate = new_record_build(data_record)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(recordToCreate).decode("UTF-8")
    response = requests.post(urlCreate, data=output, headers = headersXml)
    print(response.status_code, response.text)
    if response.status_code not in (200, 201, 409):
        with open('errorlog.txt', 'a', encoding='utf-8') as log:
            log.write(f'{response.status_code}. {response.text}\n\n')

relationOldNewIds = OrderedDict()
linksToEarlierIds = OrderedDict()  
linksToBroaderIds = OrderedDict()

def store_ids(data_record, createdCoraRecord):
    createdRecords = ET.fromstring(createdCoraRecord)
    createdRecords.findall('.//recordInfo')
    createdId = createdRecords.find('.//recordInfo/id')
    createdOldId = createdRecords.find('.//recordInfo/oldId')
    relationOldNewIds[createdOldId.text] = createdId.text
    earlierIds = data_record.find('.//earlier_id')
    if earlierIds is not None and earlierIds.text:
        earlierIdsAsList = map(str.strip, earlierIds.text.split(','))
        linksToEarlierIds[createdId.text] = earlierIdsAsList
    broaderIds = data_record.find('.//broader_id')
    if broaderIds is not None and broaderIds.text:
        linksToBroaderIds[createdId.text] = broaderIds.text
    return relationOldNewIds, linksToEarlierIds, linksToBroaderIds



start()