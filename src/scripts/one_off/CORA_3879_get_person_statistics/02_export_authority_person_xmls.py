import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from requests.help import main
from common.environment import load_environment
from common.logging_config import configure_logging

from common.threads import run_with_threads

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    status: str


def main():
    load_environment()
    configure_logging()
    _export_all_authority_person_xmls()


def _export_all_authority_person_xmls():
    fedora_url = os.environ.get("FEDORA_AUTHORITY_URL")
    person_pids = json.loads(
        Path("data/fedora/authority_person_pids.json").read_text(encoding="utf-8")
    )
    output_path = Path("data/fedora/authority_person_xml")
    output_path.mkdir(parents=True, exist_ok=True)
    run_with_threads(
        iterable=person_pids,
        function=lambda pid: _export_authority_person_xml(pid, fedora_url, output_path),
        workers=4,
        desc="Exporting authority person XMLs",
        status_order=[("SAVED", "✅"), ("SKIPPED", "⏭️"), ("FAILED", "❌")],
    )
    print(f"Saved XMLs for {len(person_pids)} PIDs to {output_path}")


def _export_authority_person_xml(pid, fedora_url, output_path):
    xml_file = output_path / f"{pid}.xml"
    if xml_file.exists():
        logger.info(f"⏭️ Skipping export for person {pid}, XML already exists")
        return ExportResult(status="SKIPPED")

    try:
        response = requests.get(f"{fedora_url}/fedora/get/{pid}/METADATA")
        response.raise_for_status()
        xml_content = response.text
        (output_path / f"{pid}.xml").write_text(xml_content, encoding="utf-8")
        logger.info(f"✅ Saved XML for person {pid}")
        return ExportResult(status="SAVED")
    except Exception as e:
        logger.error(f"❌ Failed to export person {pid}: {e}")
        return ExportResult(status="FAILED")


if __name__ == "__main__":
    main()
