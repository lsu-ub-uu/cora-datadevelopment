"""
Copyright 2025 Uppsala University Library

This file is part of DiVA Client.

    DiVA Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DiVA Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
"""

# from multiprocessing import Pool

# from multiprocessing.pool import ThreadPool
# import os
# import sys
# import threading
import time

# sys.path.append(os.path.abspath('src'))
#
# import requests
# from common.RunRotatingLogger import RunRotatingLogger
#
# from common import CommonData
# from constantsdata import ConstantsData
# from cora.client.AppTokenClient import AppTokenClient
# from tqdm import tqdm
import xml.etree.ElementTree as ET
from ids_varldskulturmuseerna import record_ids


system = "preview"
recordType = "output"
nameInData = "output"
permission_unit = "varldskulturmuseerna"
WORKERS = 16
filePath_validateBase = f"data/cora/validate/validation_order_base.xml"
# filePath_sourceXml = (f"output/{record_id}_varldskulturmuseerna.xml")

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
        dataList = read_source_xml(
            f"{record_id}_varldskulturmuserna.xml"
        )  # change to commonData
        find_validationType(list_dataRecord, dataList)


def find_validationType(list_dataRecord, dataList):
    for data_record in dataList.findall(".//publicationTypeCode"):
        list_dataRecord.append(data_record)
        print(ET.dump(data_record))
    return list_dataRecord


def read_source_xml(filePath_sourceXml):
    sourceFile_xml = ET.parse(filePath_sourceXml)
    root = sourceFile_xml.getroot()
    return root


if __name__ == "__main__":
    start()
