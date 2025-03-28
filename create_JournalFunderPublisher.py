import requests
import xml.etree.ElementTree as ET
from multiprocessing import Pool
import time
from commondata import CommonData
from secretdata import SecretData

system = 'preview'
recordType = 'diva-publisher'
WORKERS = 16
filePath_validateBase = (r"validationOrder_base.xml")
filePath_sourceXml = (r"db_xml\db_"+recordType+".xml")

def start():
    starttime = time.time()
    dataList = CommonData.read_source_xml(filePath_sourceXml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        
        test = new_publisher_build(data_record)
        print(ET.tostring(test))

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
    ET.SubElement(validationType, 'linkedRecordId').text = recordType
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

start()


