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

import xml.etree.ElementTree as ET
import requests
from typing import Callable
from common.threads import run_with_threads
from common.ssh_tunnel import SSHTunnel
from classic.config import SSH_HOST, SSH_PORT, SSH_USER

LOCAL_PORT = 8088
REMOTE_HOST = "10.0.2.68"
REMOTE_PORT = 8088


def get_classic_publications(
    pids: list[str], workers: int, on_success: Callable, on_error: Callable
):
    run_with_threads(
        pids,
        lambda pid: _get_record_by_pid(pid, on_success, on_error),
        workers=workers,
        desc="Importing publications from Classic Fedora",
    )


def _get_record_by_pid(
    pid: str,
    on_success: Callable[[str, ET.Element], None],
    on_error: Callable[[str], None],
):
    response = requests.get(
        f"http://localhost:{LOCAL_PORT}/fedora/get/{pid}/MODEL_NOREF", verify=False
    )
    response.encoding = response.apparent_encoding

    if response.status_code == 200:
        on_success(pid, ET.fromstring(response.text))
    else:
        on_error(
            f"Error fetching record {pid}: {response.status_code} - {response.text}"
        )
