
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import os
import sys
import threading
import time
sys.path.append(os.path.abspath('src'))

import requests
from common.RunRotatingLogger import RunRotatingLogger

from commondata import CommonData
from constantsdata import ConstantsData
from cora.client.AppTokenClient import AppTokenClient
from tqdm import tqdm
import xml.etree.ElementTree as ET
from collections import OrderedDict

system = 'preview'
record_type = 'diva-series'
name_in_data = 'series'
permission_unit = 'varldskulturmuseerna'
WORKERS = 16
# filer
file_path_validate_base = (r'validationOrder_base.xml')
file_path_source_xml = (r"db_xml/series_"+permission_unit+"_from_db.xml")

app_token_client = None
data_logger = None

# listor
relationOldNewIds = OrderedDict()
linksToPrecedingIds = OrderedDict()  
linksToHostIds = OrderedDict()


def start():
    global data_logger
    data_logger = RunRotatingLogger('data', 'logs/data_processing.txt').get()
    data_logger.info("Data processing started")
    starttime = time.time()
    start_app_token_client()

    dataList = CommonData.read_source_xml(file_path_source_xml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        list_dataRecord.append(data_record)
    print(f'Number of records read: {len(list_dataRecord)}')
    with ThreadPool(WORKERS) as pool:
#        list(tqdm(
#            pool.imap_unordered(new_record_build, list_dataRecord),
##            total=len(list_dataRecord),
##            desc="test records"
#        ))
        # validate
#        list(tqdm(
#            pool.imap_unordered(validate_record, list_dataRecord),
#            total=len(list_dataRecord),
#            desc="Validating records"
#        ))
        # create
        list(tqdm(
            pool.imap_unordered(create_record, list_dataRecord),
            total=len(list_dataRecord),
            desc="Created records"
        ))
        
    loop_id_lists(relationOldNewIds, linksToPrecedingIds, linksToHostIds)



def start_app_token_client():
    global app_token_client
    dependencies = {"requests": requests,
                    "time": time,
                    "threading": threading}
    app_token_client = AppTokenClient(dependencies)

    login_spec = {"login_url": ConstantsData.LOGIN_URLS[system],
            "login_id": 'divaAdmin@cora.epc.ub.uu.se',
            "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156"}
    app_token_client.login(login_spec)
    
    
def new_record_build(data_record):
    new_record_element = ET.Element(name_in_data)
    CommonData.record_info_build(name_in_data, permission_unit, data_record, new_record_element)
    CommonData.title_info_build(data_record, new_record_element)
    CommonData.titleInfo_alternative_build(data_record, new_record_element,  'alternative')
    CommonData.end_date_build(data_record, new_record_element, 'originInfo')
    CommonData.location_build(data_record, new_record_element)
    CommonData.note_build(data_record, new_record_element, 'external')
    counter = 0
    counter = CommonData.identifier_build(data_record, new_record_element, 'pissn', counter)
    counter = CommonData.identifier_build(data_record, new_record_element, 'eissn', counter)
    counter = CommonData.genre_build(data_record, new_record_element, publication_map, counter)
    orgLink_build(new_record_element, data_record)
    return new_record_element

def validate_record(data_record):
    global app_token_client
    global data_logger
    
    auth_token = app_token_client.get_auth_token()
    validate_headers_xml = {'Content-Type':'application/vnd.cora.workorder+xml',
                            'Accept':'application/vnd.cora.record+xml', 'authToken':auth_token}
    validate_url = ConstantsData.BASE_URL[system] + 'workOrder'
    newRecordToCreate = new_record_build(data_record)
    oldId_fromSource = CommonData.get_oldId(data_record)
    newRecordToValidate = CommonData.validateRecord_build(name_in_data, file_path_validate_base, newRecordToCreate)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(newRecordToValidate).decode("UTF-8")
    response = requests.post(validate_url, data=output, headers=validate_headers_xml)
#    print(response.status_code, response.text)
    if '<valid>true</valid>' not in response.text:
        data_logger.error(f"{oldId_fromSource}: {response.status_code}. {response.text}")
    if response.text:
        data_logger.info(f"{oldId_fromSource}: {response.status_code}. {response.text}")

def create_record(data_record):
    global app_token_client
    global data_logger
    
    auth_token = app_token_client.get_auth_token()
    headersXml = {'Content-Type':'application/vnd.cora.recordgroup+xml',
                  'Accept':'application/vnd.cora.record+xml', 'authToken':auth_token}
    urlCreate = ConstantsData.BASE_URL[system] + record_type
    recordToCreate = new_record_build(data_record)
    oldId_fromSource = CommonData.get_oldId(data_record)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(recordToCreate).decode("UTF-8")
    response = requests.post(urlCreate, data=output, headers=headersXml)
    print(response.status_code, response.text)
    if response.text:
        data_logger.info(f"{oldId_fromSource}: {response.status_code}. {response.text}")
    if response.status_code not in ([201]):
        data_logger.error(f"{oldId_fromSource}: {response.status_code}. {response.text}")
#    return response.text
    relationOldNewIds,linksToPrecedingIds, linksToHostIds = store_ids(data_record, response.text)
    print(f"relation: {relationOldNewIds}")
    print(f"pre: {linksToPrecedingIds}")
    print(f"host: {linksToHostIds}")
    


def store_ids(data_record, createdCoraRecord):
    createdRecords = ET.fromstring(createdCoraRecord)
    createdRecords.findall('.//recordInfo')
    createdId = createdRecords.find('.//recordInfo/id')
    createdOldId = createdRecords.find('.//recordInfo/oldId')
    relationOldNewIds[createdOldId.text] = createdId.text
    precedingIds = data_record.find('.//relative_id_preceding')
    if precedingIds is not None and precedingIds.text:
        precedingIdsAsList = map(str.strip, precedingIds.text.split(','))
        linksToPrecedingIds[createdId.text] = precedingIdsAsList
    hostIds = data_record.find('.//relative_id_host')
    if hostIds is not None and hostIds.text:
        linksToHostIds[createdId.text] = hostIds.text
    return relationOldNewIds, linksToPrecedingIds, linksToHostIds


def loop_id_lists(relationOldNewIds, linksToPrecedingIds, linksToHostIds):
    starttime = time.time()
    for oldId, newId in relationOldNewIds.items():
        if newId in linksToPrecedingIds or newId in linksToHostIds:
            repeatId = 0
            newRecord = read_record_as_xml(newId)
            cleanedRecord = CommonData.remove_actionLinks_from_record(newRecord, name_in_data)
            if newId in linksToHostIds:
                parentOldId = linksToHostIds[newId]
                parentNewId = relationOldNewIds[parentOldId]
                related_subject_build(record_type, cleanedRecord, 'host', repeatId, parentNewId)
                repeatId +=1
            if newId in linksToPrecedingIds:
                earlierOldIds = linksToPrecedingIds[newId]
                for earlierOldId in earlierOldIds: 
                    earlierNewId = relationOldNewIds[earlierOldId]
                    related_subject_build(record_type, cleanedRecord, 'preceding', repeatId, earlierNewId)
                    repeatId +=1
            update_created_record(newId, cleanedRecord)
            print()
            print(newId, earlierOldId)
            
    print(f'Tidsåtgång: {time.time() - starttime}')

def related_subject_build(record_type, cleanedRecord, relatedType, counter, value): 
    related = ET.SubElement(cleanedRecord, 'related', repeatId=str(counter), type = relatedType)
    related_series = ET.SubElement(related, 'series')
    ET.SubElement(related_series, 'linkedRecordType').text = record_type
    ET.SubElement(related_series, 'linkedRecordId').text = value

def read_record_as_xml(id):
    global app_token_client
    global data_logger
    
    auth_token = app_token_client.get_auth_token()
    headersXml = {'Content-Type':'application/vnd.cora.recordgroup+xml',
                  'Accept':'application/vnd.cora.record+xml', 'authToken':auth_token}
    getRecordUrl = ConstantsData.BASE_URL[system]+'diva-series/'+id
    response = requests.get(getRecordUrl, headers=headersXml)
    return ET.fromstring(response.text)

def update_created_record(id, recordToUpdate):
    global app_token_client
    global data_logger
    
    auth_token = app_token_client.get_auth_token()
    headersXml = {'Content-Type':'application/vnd.cora.recordgroup+xml',
                  'Accept':'application/vnd.cora.record+xml', 'authToken':auth_token}
    recordUrl = ConstantsData.BASE_URL[system]+"diva-series/"+id
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(recordToUpdate).decode("UTF-8")
    response = requests.post(recordUrl, data=output, headers = headersXml)
    print(response.status_code, response.text)
    if response.text:
        data_logger.info(f"{response.status_code}. {response.text}")
    if response.status_code not in ([200]):
        data_logger.error(f"{response.status_code}. {response.text}")
    return response.text

def orgLink_build(new_record_element, data_record):
    orgOldIdFromSource = data_record.find('.//organisation_id')
    if orgOldIdFromSource is not None and orgOldIdFromSource.text:
        orgOldId = orgOldIdFromSource.text
        recordFromSearch = search_query_org_oldId(orgOldId)
        dataList = ET.fromstring(recordFromSearch)
        idToLink = dataList.find('.//recordInfo/id')
        if idToLink is not None and idToLink.text:
            relatedOrganisation = ET.SubElement(new_record_element, 'organisation')
            ET.SubElement(relatedOrganisation, 'linkedRecordType').text = 'diva-organisation'
            ET.SubElement(relatedOrganisation, 'linkedRecordId').text = idToLink.text

def search_query_org_oldId(orgOldId):
    global app_token_client
    global data_logger
    
    auth_token = app_token_client.get_auth_token()
    search_headers_xml = {'Accept':'application/vnd.cora.recordList+xml','authToken':auth_token}
    oldId_search_query = 'searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"oldIdSearchTerm","value":"'+orgOldId+'"}]}]}]}'
    search_url = ConstantsData.BASE_URL[system]+"searchResult/diva-organisationSearch?"+oldId_search_query
    response = requests.get(search_url, headers=search_headers_xml)
    return response.text


publication_map = {
    '50': 'publication_journal-article',
    '51': 'publication_review-article',
    '52': 'publication_book-review',
    '53': 'publication_doctoral-thesis-compilation', 
    '54': 'publication_doctoral-thesis-monograph',
    '55': 'publication_licentiate-thesis-compilation',
    '56': 'publication_licentiate-thesis-monograph',
    '57': 'publication_book',
    '58': 'publication_book-chapter',
    '59': 'conference_paper', 
    '60': 'conference_proceeding',
    '61': 'intellectual-property_patent',
    '62': 'publication_report', 
    '63': 'publication_edited-book',
    '64': 'publicationPreprintItem',
    '65': 'diva_degree-project',
    '66': 'publication_other',
    '67': 'diva_dissertation',
    '71': 'artistic-work_original-creative-work'
}

if __name__ == "__main__":
    start()
