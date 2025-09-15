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

import os
import xml.etree.ElementTree as ET
import requests
from fabric import Connection
from common.threads import run_with_threads
from common.xml_utils import save_to_file

LOCAL_PORT = 8088
REMOTE_HOST = "10.0.2.68"
REMOTE_PORT = 8088


def get_publications_from_fedora(
    ssh_connection: Connection,
    pids: list[str],
    dirname: str,
    workers=16,
) -> list[ET.Element]:
    """
    Downloads a publication from Fedora by its PID and saves it to a file.
    Also downloads any attachments associated with the publication.
    """
    with ssh_connection.forward_local(
        local_port=LOCAL_PORT, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT
    ):
        return run_with_threads(
            pids,
            lambda pid: _get_publication_by_pid(pid, dirname),
            workers=workers,
            desc="Fetching publications from Fedora",
        )


def _get_publication_by_pid(pid: str, dirname: str) -> ET.Element:
    response = requests.get(
        f"http://localhost:{LOCAL_PORT}/fedora/get/{pid}/MODEL_NOREF",
    )
    response.encoding = response.apparent_encoding

    if response.status_code == 200:
        record = ET.fromstring(response.text)
        save_to_file(record, f"{dirname}/{pid}.xml")
        _download_attachments(record, pid, dirname)
        return record
    else:
        raise Exception(
            f"Error fetching record {pid}: {response.status_code} - {response.text}"
        )


def _download_attachments(publication: ET.Element, pid: str, dirname: str) -> None:
    attachments = publication.findall(".//attachment")
    for attachment in attachments:
        file_name = attachment.findtext("./fileName")
        file_suffix = attachment.findtext("./mimeType/fileSuffix")

        response = requests.get(
            f"http://localhost:{LOCAL_PORT}/fedora/get/{pid}/{file_name}"
        )
        print(f"Fetched attachment {file_name}")
        print(response.status_code)
        os.makedirs(f"{dirname}/binaries/{pid}", exist_ok=True)
        with open(f"{dirname}/binaries/{pid}/{file_name}.{file_suffix}", "wb") as f:
            f.write(response.content)
