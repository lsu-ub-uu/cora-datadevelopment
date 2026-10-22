import os
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from common.common_data import read_source_xml
from common.xml_utils import pretty_print_xml
from common.test_helper import assert_equal_for_xml_and_xml_string

xml_dir = "data/fedora_xml/polar/2026-10-22T09:00:07.862966"
path_to_look_for = ".//authorityPid"


def main():
    match_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/find_tag_{timestamp}.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    source_records = _read_source_records(xml_dir)

    for record in source_records:
        parent_map = {child: parent for parent in record.iter() for child in parent}
        tags_found = record.findall(path_to_look_for)
        for tag in tags_found:
            tag_path = _get_element_path(tag, record, parent_map)
            if len(tag) > 0:
                match_count += 1
                logging.info(
                    f"[{record.findtext('pid')}] Found match at path {tag_path} with child elements: {[child.tag for child in tag]}"
                )

                logging.info(pretty_print_xml(tag))
            elif tag.text is not None:
                match_count += 1
                msg = f"[{record.findtext('pid')}] Found match at path {tag_path} with text: {tag.text}"
                print(msg)
                logging.info(msg)
            logging.info(f"Import source: {record.findtext('.//importSource') }")
            logging.info(
                f"PublicationType: {record.findtext('./publicationType/publicationTypeCode') }"
            )

    summary = f"\nFound {match_count} tags matching {path_to_look_for}"
    print(summary)
    logging.info(summary)


def _get_element_path(
    element: ET.Element,
    root: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
) -> str:
    path_parts = []
    current = element

    while current is not root:
        parent = parent_map[current]
        tag = current.tag
        siblings = [child for child in parent if child.tag == tag]
        if len(siblings) > 1:
            tag = f"{tag}[{siblings.index(current) + 1}]"
        path_parts.append(tag)
        current = parent

    return "./" + "/".join(reversed(path_parts))


def _read_source_records(xml_dir: str) -> list[ET.Element]:
    records = [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]
    return records


if __name__ == "__main__":
    main()
