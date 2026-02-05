import os
import xml.etree.ElementTree as ET
from common.common_data import read_source_xml

xml_dir = "data/fedora_xml/uu/2025-08-28T10:08:51.918238"
path_to_look_for = "./administrativeInfo/fileUploadMessage"


def main():
    match_count = 0
    source_records = _read_source_records(xml_dir)
    for record in source_records:
        tags_found = record.findall(path_to_look_for)
        for tag in tags_found:
            if len(tag) > 0:
                match_count += 1
                print(
                    f"[{record.findtext('pid')}] Found match with child elements: {[child.tag for child in tag]}"
                )
            elif tag.text is not None:
                match_count += 1
                print(f"[{record.findtext('pid')}] Found match with text: {tag.text}")

    print(f"\nFound {match_count} tags matching {path_to_look_for}")


def _read_source_records(xml_dir: str) -> list[ET.Element]:
    records = [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]
    return records


if __name__ == "__main__":
    main()
