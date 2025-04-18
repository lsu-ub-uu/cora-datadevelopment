import xml.etree.ElementTree as ET
import requests
import time
import threading
from multiprocessing import Pool
from secretdata import SecretData
from commondata import CommonData
from constantsdata import ConstantsData
#from serversidedata import ServersideData
from tqdm import tqdm
import sys
import os


sys.path.append(os.path.abspath('src'))
from cora.client.AppTokenClient import AppTokenClient

system = 'preview'
#system = 'local'
recordType = 'journal'
WORKERS = 4
filePath_validateBase = (r"validationOrder_base.xml")
# filePath_sourceXml = (r"db_xml\db_diva-"+recordType+".xml")
filePath_sourceXml = (r"db_xml/journal_from_db.xml")

request_counter = 0
app_token_client = None

def start():
    starttime = time.time()
    start_app_token_client()
    
    dataList = CommonData.read_source_xml(filePath_sourceXml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        list_dataRecord.append(data_record)
    
    print(f'Number of records read: {len(list_dataRecord)}')

    
    with Pool(WORKERS) as pool:
#        test = pool.map(new_record_build, list_dataRecord)
#            print(test)
#        pool.map(validate_record, list_dataRecord)
        list(tqdm(
            pool.imap_unordered(validate_record, list_dataRecord),
            total=len(list_dataRecord),
            desc="Validating records"
        ))
#        list(tqdm(
#            pool.imap_unordered(create_record, list_dataRecord),
#            total=len(list_dataRecord),
#            desc="Validating records"
#        ))
        # pool.map(ServersideData.create_record, list_dataRecord)

    print(f'Tidsåtgång: {time.time() - starttime}')
    
def start_app_token_client():
    global app_token_client
    login_urls = {
        'local': 'http://localhost:8182/',
        'preview': 'https://cora.epc.ub.uu.se/diva/',
        'mig': 'https://mig.diva-portal.org/',
        'pre': 'https://pre.diva-portal.org/',
    }
    dependencies = {"requests": requests,
                             "time": time,
                             "threading": threading}
    app_token_client = AppTokenClient(dependencies)

    login_spec = {"login_url": login_urls[system]+'login/rest/apptoken',
            "login_id": 'divaAdmin@cora.epc.ub.uu.se',
            "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156"}
    app_token_client.login(login_spec)

def new_record_build(data_record):
        newRecordElement = ET.Element(recordType)
        CommonData.recordInfo_build(recordType, data_record, newRecordElement)
        CommonData.titleInfo_build(data_record, newRecordElement)
        counter = 0
        counter = CommonData.identifier_build(data_record, newRecordElement, 'pissn', counter)
        counter = CommonData.identifier_build(data_record, newRecordElement, 'eissn', counter)
        CommonData.endDate_build(data_record, newRecordElement, 'originInfo')
        CommonData.location_build(data_record, newRecordElement)
        return newRecordElement

def validate_record(data_record):
#    authToken = SecretData.get_authToken(system)
    global app_token_client
    authToken = app_token_client.get_auth_token()
    validate_headers_xml = {'Content-Type':'application/vnd.uub.workorder+xml',
                            'Accept':'application/vnd.uub.record+xml','authToken':authToken}
    validate_url = ConstantsData.BASE_URL[system]+'workOrder'
    newRecordToCreate = new_record_build(data_record)
    oldId_fromSource = CommonData.get_oldId(data_record)
    newRecordToValidate = CommonData.validateRecord_build(recordType, filePath_validateBase, newRecordToCreate)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(newRecordToValidate).decode("UTF-8")
    response = requests.post(validate_url, data=output, headers = validate_headers_xml)
#    print(response.status_code, response.text)
    if '<valid>true</valid>' not in response.text:
        with open(f'errorlog.txt', 'a', encoding='utf-8') as log:
            log.write(f"{oldId_fromSource}: {response.status_code}. {response.text}\n\n")
    if response.text:
        with open(f'log.txt', 'a', encoding='utf-8') as log:
            log.write(f"{oldId_fromSource}: {response.status_code}. {response.text}\n\n")


def create_record(data_record):
#    authToken = SecretData.get_authToken(system)
    global app_token_client
    authToken = app_token_client.get_auth_token()
    headersXml = {'Content-Type':'application/vnd.uub.record+xml',
                  'Accept':'application/vnd.uub.record+xml', 'authToken':authToken}
    urlCreate = ConstantsData.BASE_URL[system]+"diva-"+recordType
    recordToCreate = new_record_build(data_record)
    output = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"+ET.tostring(recordToCreate).decode("UTF-8")
    response = requests.post(urlCreate, data=output, headers = headersXml)
#    print(response.status_code, response.text)
    if response.status_code not in (200, 201, 409):
        with open('errorlog.txt', 'a', encoding='utf-8') as log:
            log.write(f'{response.status_code}. {response.text}\n\n')
    return response.text

if __name__ == "__main__":
    start()