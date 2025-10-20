import xml.etree.ElementTree as ET
import requests
from classic.config import SSH_HOST, SSH_PORT, SSH_USER
from common.ssh_tunnel import SSHTunnel

LOCAL_PORT = 8080

# REMOTE_HOST = "diva-node4"
# REMOTE_PORT = 8080
# SOLR_SEARCH_URL = f"http://localhost:{LOCAL_PORT}/diva-search/diva/select"

REMOTE_HOST = "diva-node7"
REMOTE_PORT = 8083
SOLR_SEARCH_URL = f"http://localhost:{LOCAL_PORT}/solr-admin/dream/select"


def get_pids_for_domain(domain: str) -> list[str]:
    with SSHTunnel(SSH_HOST, SSH_PORT, SSH_USER, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT):
        number_of_records_response = requests.get(
            f"{SOLR_SEARCH_URL}?q=domain%3A{domain}&start=0&rows=0&wt=xml&indent=true"
        )

        number_of_records_response.raise_for_status()

        result = ET.fromstring(number_of_records_response.text).find("result")

        assert result is not None, "No result element found in response"
        number_of_records = result.get("numFound")
        get_pids_response = requests.get(
            f"{SOLR_SEARCH_URL}?q=*%3A*&fq=domain%3A{domain}&rows={number_of_records}&fl=PID&wt=xml&indent=true"
        )

        get_pids_response.raise_for_status()
        pids = [
            pid.text
            for pid in ET.fromstring(get_pids_response.text).findall(
                "./result/doc/str[@name='PID']"
            )
            if pid.text is not None
        ]
        return pids

    return []
