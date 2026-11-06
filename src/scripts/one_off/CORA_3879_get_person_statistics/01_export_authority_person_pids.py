import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from requests.help import main
from common.environment import load_environment
from common.logging_config import configure_logging


def main():
    load_environment()
    configure_logging()
    _export_all_authority_person_pids()


def _export_all_authority_person_pids():
    person_pids = _get_all_authority_person_pids()
    output_path = Path("data/fedora/authority_person_pids.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(person_pids, indent=2), encoding="utf-8")
    print(f"Saved {len(person_pids)} PIDs to {output_path}")


def _get_all_authority_person_pids():
    fedora_url = os.environ.get("FEDORA_AUTHORITY_URL")
    assert (
        fedora_url is not None
    ), "FEDORA_AUTHORITY_URL environment variable is not set"

    first_page_response = requests.get(
        f"{fedora_url}/fedora/search?query=pid~authority-person%3A*&pid=true&maxResults=1000&xml=true"
    )

    first_page_response.raise_for_status()
    text = first_page_response.text
    xml = ET.fromstring(text)
    pids = [
        element.text for element in xml.findall(".//{*}pid") if element.text is not None
    ]
    print("pids", len(pids))

    session_token = xml.findtext(".//{*}token")
    while session_token:
        next_page_response = requests.get(
            f"{fedora_url}/fedora/search?query=pid~authority-person%3A*&pid=true&maxResults=1000&xml=true&sessionToken={session_token}"
        )
        next_page_response.raise_for_status()
        next_page_text = next_page_response.text
        next_page_xml = ET.fromstring(next_page_text)
        pids.extend(
            [
                element.text
                for element in next_page_xml.findall(".//{*}pid")
                if element.text is not None
            ]
        )
        session_token = next_page_xml.findtext(".//{*}token")
        print("fetched new page. pids:", len(pids))
    print("total pids", len(pids))
    return sorted(pids, key=lambda pid: int(pid.split(":")[1]))


if __name__ == "__main__":
    main()
