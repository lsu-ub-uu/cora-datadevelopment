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


from sshtunnel import SSHTunnelForwarder
import requests

# record_ids = [1775040, 1703518, 1707279, 1681782, 1781879]
record_ids = []

ssh_host = "130.238.7.110"
ssh_port = 22
ssh_user = "support"
ssh_password = None
REMOTE_HOST = "diva-node4"
REMOTE_PORT = 8080


server = SSHTunnelForwarder(
    (ssh_host, ssh_port),
    ssh_username=ssh_user,
    host_pkey_directories=["~/.ssh"],
    remote_bind_address=(REMOTE_HOST, REMOTE_PORT)
)

server.start()

response = requests.get(
    f"http://localhost:{server.local_bind_port}/diva-search/diva/select?q=domain%3Avarldskulturmuseerna&start=0&rows=0&wt=xml&indent=true",
)
print(response.text)

server.stop()