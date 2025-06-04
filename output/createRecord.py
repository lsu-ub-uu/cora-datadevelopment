#from multiprocessing import Pool
#from multiprocessing.pool import ThreadPool
#import os
#import sys
#import threading
import time
#sys.path.append(os.path.abspath('src'))
#
#import requests
#from common.RunRotatingLogger import RunRotatingLogger
#
#from commondata import CommonData
#from constantsdata import ConstantsData
#from cora.client.AppTokenClient import AppTokenClient
#from tqdm import tqdm
import xml.etree.ElementTree as ET
from ids_varldskulturmuseerna import record_ids


system = 'preview'
recordType = 'output'
nameInData = 'output'
permission_unit = 'varldskulturmuseerna'
WORKERS = 16
filePath_validateBase = (f"validationOrder_base.xml")
#filePath_sourceXml = (f"output/{record_id}_varldskulturmuseerna.xml")

request_counter = 0
app_token_client = None
data_logger = None


def start():
    global data_logger
#    data_logger = RunRotatingLogger('data', 'logs/data_processing.txt').get()
#    data_logger.info("Data processing started")
    starttime = time.time()
#    start_app_token_client()
#
    list_dataRecord = []
    for record_id in record_ids:
        dataList = read_source_xml(f"{record_id}_varldskulturmuserna.xml") # change to commonData
        find_validationType(list_dataRecord, dataList)


def find_validationType(list_dataRecord, dataList):
    for data_record in dataList.findall('.//publicationTypeCode'):
        list_dataRecord.append(data_record)
        print(ET.dump(data_record))
    return list_dataRecord

def read_source_xml(filePath_sourceXml):
    sourceFile_xml = ET.parse(filePath_sourceXml)
    root = sourceFile_xml.getroot()
    return root

if __name__ == "__main__":
    start()
    
    
    