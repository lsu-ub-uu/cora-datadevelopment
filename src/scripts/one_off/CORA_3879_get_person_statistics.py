import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from requests.help import main
from common.environment import load_environment
from common.logging_config import configure_logging
import time


def main():
    load_environment()
    configure_logging()
    # export_all_authority_person_pids()
    export_all_authority_person_xmls()


def export_all_authority_person_xmls():
    fedora_url = os.environ.get("FEDORA_URL")
    person_pids = json.loads(
        Path("data/fedora/authority_person_pids.json").read_text(encoding="utf-8")
    )
    output_path = Path("data/fedora/authority_person_xml")
    output_path.mkdir(parents=True, exist_ok=True)
    for pid in person_pids:
        response = requests.get(f"{fedora_url}/fedora/get/{pid}/METADATA")
        response.raise_for_status()
        xml_content = response.text
        (output_path / f"{pid}.xml").write_text(xml_content, encoding="utf-8")
        print(f"Saved XML {output_path}/{pid}.xml")
        time.sleep(0.1)  # Add a delay to avoid overwhelming the server
    print(f"Saved XMLs for {len(person_pids)} PIDs to {output_path}")


def export_all_authority_person_pids():
    person_pids = _get_all_authority_person_pids()
    output_path = Path("data/fedora/authority_person_pids.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(person_pids, indent=2), encoding="utf-8")
    print(f"Saved {len(person_pids)} PIDs to {output_path}")


def _get_all_authority_person_pids():
    fedora_url = os.environ.get("FEDORA_URL")
    assert fedora_url is not None, "FEDORA_URL environment variable is not set"

    first_page_response = requests.get(
        f"{fedora_url}/fedora/search?query=pid~authority-person%3A*&pid=true&maxResults=1000&xml=true"
    )

    first_page_response.raise_for_status()
    text = first_page_response.text
    xml = ET.fromstring(text)
    pids = [element.text for element in xml.findall(".//{*}pid")]
    print("pids", len(pids))

    session_token = xml.findtext(".//{*}token")
    while session_token:
        next_page_response = requests.get(
            f"{fedora_url}/fedora/search?query=pid~authority-person%3A*&pid=true&maxResults=1000&xml=true&sessionToken={session_token}"
        )
        next_page_response.raise_for_status()
        next_page_text = next_page_response.text
        next_page_xml = ET.fromstring(next_page_text)
        pids.extend([element.text for element in next_page_xml.findall(".//{*}pid")])
        session_token = next_page_xml.findtext(".//{*}token")
        time.sleep(0.1)  # Add a delay to avoid overwhelming the server
        print("fetched new page. pids:", len(pids))
    print("total pids", len(pids))
    # Iamplement the logic to retrieve all authority person PIDs
    return pids


if __name__ == "__main__":
    main()
