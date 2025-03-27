import requests
from multiprocessing import Pool
import time
import xml.etree.ElementTree as ET
from commondata import CommonData
from secretdata import SecretData

system = 'preview'
validationType = 'diva-funder'
WORKERS = 16



filePath_validateBase = (r"C:\Users\sarto903\Documents\Python\validationOrder_base.xml")
filePath_sourceXml = (r"C:\Users\sarto903\Documents\Python\db_xml\db_"+validationType+".xml")


def start():
    starttime = time.time()
    dataList = CommonData.read_source_xml(filePath_sourceXml)
    list_dataRecord = []
    for data_record in dataList.findall('.//DATA_RECORD'):
        print(data_record)
    print(f'Tidsåtgång: {time.time() - starttime}')
start()

