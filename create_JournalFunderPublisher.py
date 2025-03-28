import requests
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import time
from commondata import CommonData
from secretdata import SecretData

system = 'preview'
recordType = 'publisher'
WORKERS = 16
filePath_validateBase = (r"validationOrder_base.xml")
filePath_sourceXml = (r"db_xml\db_diva-"+recordType+".xml")

def start():
    starttime = time.time()
    dataList = CommonData.read_source_xml(filePath_sourceXml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        
        """ test = new_publisher_build(data_record)
        print(ET.tostring(test))"""
        validate_record(data_record)

    print(f'Tidsåtgång: {time.time() - starttime}')



def new_journal_build(data_record):
        newRecord = ET.Element(recordType)
        recordInfo_build(recordType, data_record, newRecord)
        name_build(data_record, newRecord, 'authority', 'swe')
        name_build(data_record, newRecord, 'variant', 'eng')
        identifier_build(data_record, newRecord, 'doi')
        identifier_build(data_record, newRecord, 'organisationNumber')
        endDate_build(data_record, newRecord)
        return newRecord

def new_funder_build(data_record):
        newRecord = ET.Element(recordType)
        recordInfo_build(recordType, data_record, newRecord)
        # name_build(data_record, newRecord, 'authority', 'swe')
        # name_build(data_record, newRecord, 'variant', 'eng')
        # identifier_build(data_record, newRecord, 'doi')
        # identifier_build(data_record, newRecord, 'organisationNumber')
        # endDate_build(data_record, newRecord)
        return newRecord

def new_publisher_build(data_record):
        newRecordElement = ET.Element(recordType)
        recordInfo_build(recordType, data_record, newRecordElement)
        name_build(data_record, newRecordElement)
        return newRecordElement

def recordInfo_build(recordType, data_record, newRecordElement):
    recordInfo = ET.SubElement(newRecordElement, 'recordInfo')
    validationType = ET.SubElement(recordInfo, 'validationType')
    ET.SubElement(validationType, 'linkedRecordType').text = 'validationType'
    ET.SubElement(validationType, 'linkedRecordId').text = "diva-"+recordType
    dataDivider = ET.SubElement(recordInfo, 'dataDivider')
    ET.SubElement(dataDivider, 'linkedRecordType').text = 'system'
    ET.SubElement(dataDivider, 'linkedRecordId').text = 'divaData'
    oldId_fromSource = data_record.find('.//old_id')
    ET.SubElement(recordInfo, 'oldId').text = oldId_fromSource.text

def name_build(data_record, newRecordElement):
    name_fromSource = data_record.find('.//name')
    if name_fromSource is not None and name_fromSource.text:
        name = ET.SubElement(newRecordElement, 'name', type = 'corporate')
        ET.SubElement(name, 'namePart').text = name_fromSource.text

def validateRecord_build(recordType, filePath_validateBase, newRecordToCreate):
    # validationOrder_baseFile = ET.parse(filePath_validateBase)
    # validationOrder_root = validationOrder_baseFile.getroot()
    validationOrder_root = CommonData.read_source_xml(filePath_validateBase)
    validationOrder_root.find('.//recordType/linkedRecordId').text = "diva-"+recordType
    validationOrder_root.find('.//validateLinks').text = 'false'
    validationOrder_root.find('.//metadataToValidate').text = 'new'
    record = validationOrder_root.find('.//record')
    record.append(newRecordToCreate)
    return validationOrder_root

def validate_record(data_record):
    authToken = SecretData.get_authToken(system)
    validate_headers_xml = {'Content-Type':'application/vnd.uub.workorder+xml', 'Accept':'application/vnd.uub.record+xml','authToken':authToken}
    validate_url = 'https://cora.epc.ub.uu.se/diva/rest/record/workOrder'
    newRecordToCreate = new_publisher_build(data_record)
    newRecordToValidate = validateRecord_build(recordType, filePath_validateBase, newRecordToCreate)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(newRecordToValidate).decode("UTF-8")
    response = requests.post(validate_url, data=output, headers = validate_headers_xml)
    print(response.status_code, response.text)
    if '<valid>true</valid>' not in response.text:
        with open(f'errorlog.txt', 'a', encoding='utf-8') as log:
            log.write(f"{response.status_code}. {response.text}\n\n")




start()


