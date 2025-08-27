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

LOCAL_PORT = 8080
REMOTE_HOST = "diva-node4"
REMOTE_PORT = 8080

def get_record_by_pid(pid: str, connection: Connection) -> ET.Element:
    with connection.forward_local(local_port=LOCAL_PORT, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT):
        response = requests.get(
            f"https://localhost:{LOCAL_PORT}/fedora/get/{pid}/MODEL_NOREF", verify=False
        )
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return ET.fromstring(response.text)
        else:
            raise Exception(
                f"Error fetching record {pid}: {response.status_code} - {response.text}"
            )
