from pathlib import Path

from common.threads import run_with_threads
import xml.etree.ElementTree as ET

XML_DIR = Path("data/fedora/authority_person_xml")


def main():
    print(f"Checking XML files in {XML_DIR}")
    xml_files = list(XML_DIR.glob("*.xml"))
    if not xml_files:
        raise SystemExit("No XML files found")
    print(f"Found {len(xml_files)} XML files")

    results = run_with_threads(
        xml_files, _check_xml, desc="Checking for nonpublic records"
    )

    for pid in [result for result in results if result is not None]:
        print(pid)


def _check_xml(xml_path):
    root = ET.parse(xml_path, parser=ET.XMLParser(encoding="utf-8")).getroot()
    public_record = root.findtext("./publicRecord")
    if public_record == "false":
        return root.findtext("./pid")
    return None


if __name__ == "__main__":
    main()
