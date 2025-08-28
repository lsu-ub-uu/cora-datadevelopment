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

from fabric import Connection

import xml.etree.ElementTree as ET
import requests
import urllib3
from common.xml_utils import pretty_print_xml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_record_by_pid(pid: str) -> ET.Element:
    response = requests.get(
        f"https://uu.diva-portal.org:8443/fedora/get/{pid}/MODEL_NOREF", verify=False
    )
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        return ET.fromstring(response.text)
    else:
        raise Exception(
            f"Error fetching record {pid}: {response.status_code} - {response.text}"
        )
