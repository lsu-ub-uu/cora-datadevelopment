import xml.etree.ElementTree as ET
import requests


def get_pids_for_domain(domain: str, *, solr_url: str) -> list[str]:
    number_of_records_response = requests.get(
        f"{solr_url}?q=domain%3A{domain}&start=0&rows=0&wt=xml&indent=true"
    )

    number_of_records_response.raise_for_status()

    result = ET.fromstring(number_of_records_response.text).find("result")

    assert result is not None, "No result element found in response"
    number_of_records = result.get("numFound")
    get_pids_response = requests.get(
        f"{solr_url}?q=*%3A*&fq=domain%3A{domain}&rows={number_of_records}&fl=PID&wt=xml&indent=true"
    )

    get_pids_response.raise_for_status()
    pids = [
        pid.text
        for pid in ET.fromstring(get_pids_response.text).findall(
            "./result/doc/str[@name='PID']"
        )
        if (pid.text is not None) and ("draft" not in pid.text)
    ]
    return pids
