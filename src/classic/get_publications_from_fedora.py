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

from collections.abc import Callable
import xml.etree.ElementTree as ET
import requests
from fabric import Connection
from common.threads import run_with_threads

LOCAL_PORT = 8088
REMOTE_HOST = "10.0.2.68"
REMOTE_PORT = 8088


def get_publications_from_fedora(
    ssh_connection: Connection,
    pids: list[str],
    on_export: Callable[[ET.Element], None],
    workers=16,
) -> list[ET.Element]:
    with ssh_connection.forward_local(
        local_port=LOCAL_PORT, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT
    ):
        return run_with_threads(
            pids,
            lambda pid: _get_publication_by_pid(pid, on_export),
            workers=workers,
            desc="Fetching publications from Fedora",
        )


def _get_publication_by_pid(
    pid: str, on_import: Callable[[ET.Element], None]
) -> ET.Element:
    response = requests.get(
        f"http://localhost:{LOCAL_PORT}/fedora/get/{pid}/MODEL_NOREF",
    )

    if response.status_code == 200:
        result = ET.fromstring(response.text)
        on_import(result)
        return result
    else:
        raise Exception(
            f"Error fetching record {pid}: {response.status_code} - {response.text}"
        )
