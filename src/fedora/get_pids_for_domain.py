import xml.etree.ElementTree as ET
from fabric import Connection
import requests
from fedora.get_record_by_pid import get_record_by_pid

LOCAL_PORT = 8080
REMOTE_HOST = "diva-node4"
REMOTE_PORT = 8080

def get_pids_for_domain(domain: str, connection: Connection) -> list[str]:
    with connection.forward_local(local_port=LOCAL_PORT, remote_host=REMOTE_HOST, remote_port=REMOTE_PORT):
        number_of_records_response = requests.get(f"http://localhost:{LOCAL_PORT}/diva-search/diva/select?q=domain%3A{domain}&start=0&rows=0&wt=xml&indent=true")
        number_of_records = ET.fromstring(number_of_records_response.text).find('result').get('numFound')
        response = requests.get(f"http://localhost:{LOCAL_PORT}/diva-search/diva/select?q=*%3A*&fq=domain%3A{domain}&rows={number_of_records}&fl=PID&wt=xml&indent=true")
        pids = [pid.text for pid in ET.fromstring(response.text).findall("./result/doc/str[@name='PID']")]
        return pids
    
    return []


if __name__ == '__main__':
    ssh_host = "130.238.7.110"
    ssh_port = 22
    ssh_user = "support"


    with Connection(host=ssh_host, port=ssh_port,  user=ssh_user) as connection:
        pids = get_pids_for_domain('varldskulturmuseerna', connection)
        for pid in pids:
            print(get_record_by_pid(pid, connection))