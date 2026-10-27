import os
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from common.common_data import read_source_xml
from common.xml_utils import pretty_print_xml
from common.test_helper import assert_equal_for_xml_and_xml_string

xml_dir = "data/fedora_xml/polar/2025-11-13T16:16:33.561276"
# path_to_look_for = [
#     "./doi",
#     "./identifiers/entry[publicationIdentifierType='doi']/publicationIdentifier/value",
# ]
path_to_look_for = [
    "./doi",
    "./identifiers/entry[publicationIdentifierType='doi']/publicationIdentifier/value",
]


def main():
    match_count = 0
    empty_tag_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/find_tag_{timestamp}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    source_records = _read_source_records(xml_dir)

    for record in source_records:
        for path in path_to_look_for:
            tags_found = record.findall(path)
            for tag in tags_found:
                if len(tag) > 0:
                    match_count += 1
                    logging.info(
                        f"[{record.findtext('pid')}] Found match with child elements: {[child.tag for child in tag]}"
                    )

                    logging.info(pretty_print_xml(tag))
                elif tag.text is not None:
                    match_count += 1
                    msg = (
                        f"[{record.findtext('pid')}] Found match with text: {tag.text}"
                    )
                    print(msg)
                    logging.info(msg)
                elif _is_empty_tag(tag):
                    empty_tag_count += 1
                logging.info(f"Import source: {record.findtext('.//importSource') }")
                logging.info(
                    f"PublicationType: {record.findtext('./publicationType/publicationTypeCode') }"
                )

    summary = (
        f"\nFound {match_count} non-empty tags matching paths {', '.join(path_to_look_for)}, "
        f"and {empty_tag_count} empty tags"
    )
    print(summary)
    logging.info(summary)


def _is_empty_tag(tag: ET.Element) -> bool:
    return len(tag) == 0 and tag.text is None


def _read_source_records(xml_dir: str) -> list[ET.Element]:
    records = [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]
    return records


if __name__ == "__main__":
    main()
