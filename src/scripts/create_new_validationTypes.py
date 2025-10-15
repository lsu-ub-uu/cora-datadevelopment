import xml.etree.ElementTree as ET

from collections import deque
from typing import Any

import requests

BASE_URL = "http://192.168.49.2:30982/rest/record/"
TYPE_PREFIX = "XYZ_"
GLOBAL_NODE_MAP = {}
GLOBAL_ID_MAPPING = {}
TOTAL_PROCESSED_RECORDS = 0
TOTAL_UPDATES = 0
TOTAL_ERRORS = []
TOTAL_FETCHED = 0


# Represent a record and its relationships ----------------------------------
class RecordNode:
    def __init__(self, record_id, record_type, url, xml_content):
        self.record_id = record_id
        self.record_type = record_type
        self.url = url
        self.xml_content = xml_content
        self.child_urls = []
        self.children = []
        self.parents = []
        self.new_record_id = None


def main():
    validation_types = [
        # "diva-output",
        "diva_degree-project",
        "publication_doctoral-thesis-monograph",
        "publication_doctoral-thesis-compilation",
        "publication_editorial-letter",
        "publication_working-paper",
        "publication_report-chapter",
        "publication_foreword-afterword",
        "publication_newspaper-article",
        "intellectual-property_patent",
        "conference_poster",
        "publication_journal-issue",
        "artistic-work_artistic-thesis",
        "publication_book",
        "diva_dissertation",
        "artistic-work_original-creative-work",
        "conference_paper",
        "conference_other",
        "publication_magazine-article",
        "publication_book-chapter",
        "publication_encyclopedia-entry",
        "conference_proceeding",
        "publication_edited-book",
        "publication_licentiate-thesis-compilation",
        "publication_book-review",
        "publication_critical-edition",
        "publication_report",
        "publication_preprint",
        "publication_journal-article",
        "publication_licentiate-thesis-monograph",
        "publication_other",
    ]
    create_new_validation_types(validation_types)


def create_new_validation_types(root_urls):
    print("\n=== Building node map ===")
    root_urls = [BASE_URL + "validationType/" + string for string in root_urls]
    for root_url in root_urls:
        build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)

    # print_node_map_summary()

    print("\n=== Processing node map ===")
    process_node_map_bottom_up_and_store(GLOBAL_NODE_MAP, GLOBAL_ID_MAPPING)

    print("\n=== Script finished ===")
    print(f"  Total records fetched:   {TOTAL_FETCHED}")
    print(f"  Total records processed: {TOTAL_PROCESSED_RECORDS}")
    print(f"  Total records created:   {TOTAL_UPDATES}")

    if TOTAL_FETCHED != TOTAL_PROCESSED_RECORDS:
        print(f"\n>>> WARNING!! - Fetched {TOTAL_FETCHED} but only processed {TOTAL_PROCESSED_RECORDS} records.")

    if TOTAL_ERRORS:
        print("\n=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            print(f" > {error}")
    else:
        print("\nNo errors reported.")


def build_node_map_from_child_references(root_url, global_node_map):
    global TOTAL_FETCHED
    """
    - Top-level: newMetadataId + metadataId
    - Lower levels: only childReferences
    - Reuses previously fetched nodes stored in `node_map`.
    """
    if root_url in global_node_map:
        return global_node_map

    queue = deque([root_url])
    process_queue_and_collect_nodes(queue, root_url, global_node_map)
    link_parent_child_relationship(global_node_map)

    print(f"\nFetched {len(global_node_map)} unique records.")
    TOTAL_FETCHED = len(global_node_map)
    return global_node_map


def print_node_map_summary():
    print("\n=== Graph Summary ===")
    for url, node in GLOBAL_NODE_MAP.items():
        print(f"{url} → {len(node.children)} children, {len(node.parents)} parents")


def process_queue_and_collect_nodes(queue: deque[str], root_url: str, global_node_map: dict[str, RecordNode]) -> None:
    while queue:
        url = queue.popleft()
        if url in global_node_map:
            continue

        xml_text = fetch_xml_from_api(url)
        node = parse_record_from_xml(xml_text, url)
        global_node_map[url] = node

        child_urls = collect_child_urls(node, root_url, url)

        for child_url in child_urls:
            if child_url not in global_node_map:
                queue.append(child_url)


def collect_child_urls(node: RecordNode, root_url, url) -> list[Any]:
    if url == root_url:
        child_urls = find_top_level_children(node.xml_content)
    else:
        child_urls = find_child_urls(node.xml_content)

    node.child_urls = child_urls
    return child_urls


def link_parent_child_relationship(global_node_map: dict[Any, Any]):
    for node in global_node_map.values():
        for child_url in node.child_urls:
            if child_url in global_node_map:
                node.children.append(global_node_map[child_url])
                global_node_map[child_url].parents.append(node)


def process_node_map_bottom_up_and_store(global_node_map, global_id_mapping):
    """
    Kahn's algorithm for topological sorting.
    Processes nodes only after all their children have been processed.
    Detects and reports unprocessed nodes (cycles or disconnected).
    """

    # Build a map keeping track of unprocessed children
    unprocessed_child_map: dict[str, int] = {url: len(node.children) for url, node in global_node_map.items()}

    # Create a queue of leaf nodes
    leaf_queue: deque[str] = deque([url for url, count in unprocessed_child_map.items() if count == 0])

    processed: set[str] = set()

    while leaf_queue:
        child_reference_url = leaf_queue.popleft()
        node = global_node_map[child_reference_url]

        process_node(global_id_mapping, node)
        processed.add(child_reference_url)
        update_parent_dependencies(leaf_queue, node, unprocessed_child_map)

    check_for_unprocessed_nodes(global_node_map, processed)


def process_node(global_id_mapping, node):
    global TOTAL_PROCESSED_RECORDS, TOTAL_UPDATES, TOTAL_ERRORS

    try:
        TOTAL_PROCESSED_RECORDS += 1
        if process_and_possibly_save(node, global_id_mapping):
            TOTAL_UPDATES += 1
    except Exception as e:
        TOTAL_ERRORS.append(f"Error processing {node.record_id}: {e}")
        print(f"Error processing {node.record_id}: {e}")


def update_parent_dependencies(leaf_queue: deque[str], node, unprocessed_child_map: dict[str, int]):
    for parent in node.parents:
        if parent.url in unprocessed_child_map:
            unprocessed_child_map[parent.url] -= 1
            if unprocessed_child_map[parent.url] == 0:
                leaf_queue.append(parent.url)


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        print(f"\n>>> WARNING!! -  {len(unprocessed)} records were never processed:")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def process_and_possibly_save(node, global_id_mapping):
    old_id = node.record_id

    if skip_if_already_processed(node, global_id_mapping):
        return False

    updated = False
    if normalize_regex_patterns(node.xml_content):
        print(f"> Normalized regex pattern(s) to '.+' in {old_id}")
        updated = True

    if normalize_child_reference_repeat(node.xml_content):
        print(f"> Normalized childReference(s) Min Max to '0-X' in {old_id}")
        updated = True

    child_renamed = any(c.record_id in global_id_mapping for c in node.children)

    if not (updated or child_renamed):
        update_child_references(node.xml_content, global_id_mapping)
        return False

    new_id = create_new_id_and_update_mapping(global_id_mapping, node, old_id)
    update_record_id_in_xml(node.xml_content, new_id)
    update_child_references(node.xml_content, global_id_mapping)
    remove_action_links(node.xml_content)
    return prepare_and_try_to_save_record(node)


def create_new_id_and_update_mapping(global_id_mapping, node, old_id) -> str:
    new_id = f"{TYPE_PREFIX}{old_id}"
    node.new_record_id = new_id
    global_id_mapping[old_id] = new_id
    return new_id


def skip_if_already_processed(node: RecordNode, global_id_mapping: dict) -> bool:
    old_id = node.record_id
    if old_id in global_id_mapping:
        node.new_record_id = global_id_mapping[old_id]
        print(f"Skipping already processed {old_id} -> {node.new_record_id}")
        return True
    return False


def prepare_and_try_to_save_record(node):
    record_type = node.xml_content.findtext(".//recordInfo/type/linkedRecordId")

    content_root = unwrap_and_clean_xml_for_create(node.xml_content)
    xml_bytes = to_xml_bytes(content_root)

    base_url = f"{BASE_URL}"
    record_type_url = f"{base_url}{record_type}"

    print(f">>> Creating {node.new_record_id} ({record_type})...")
    print(f"  Endpoint: {record_type_url}")
    print("  Payload: " + xml_bytes.decode("utf-8"))

    return try_to_store_record(node, record_type_url, xml_bytes)


# XML utilities ----------------------------------
def normalize_regex_patterns(xml_root):
    updated = False
    for tag in ("regex", "regEx", "pattern"):
        for element in xml_root.findall(f".//{tag}"):
            if element.text and element.text.strip() not in (None, ".+"):
                element.text = ".+"
                updated = True
    return updated


def normalize_child_reference_repeat(xml_root):
    updated = False
    for child_reference in xml_root.findall(".//childReferences/childReference"):
        repeat_min_element = child_reference.find("repeatMin")
        repeat_max_element = child_reference.find("repeatMax")

        if repeat_min_element is not None and repeat_min_element.text != "0":
            repeat_min_element.text = "0"
            updated = True
        if repeat_max_element is not None and repeat_max_element.text != "X":
            repeat_max_element.text = "X"
            updated = True
    return updated


def update_child_references(xml_root, id_mapping):
    for element in xml_root.findall(".//linkedRecordId"):
        old_id = (element.text or "").strip()
        if old_id in id_mapping:
            element.text = str(id_mapping[old_id])


def update_record_id_in_xml(xml_root, new_id):
    id_element = xml_root.find(".//recordInfo/id")
    if id_element is not None:
        id_element.text = new_id


def remove_action_links(xml_root):
    for parent in xml_root.iter():
        for child in parent:
            if child.tag == "actionLinks":
                parent.remove(child)


def parse_record_from_xml(xml_text, url):
    root = ET.fromstring(xml_text)
    record_info = root.find(".//recordInfo")
    record_id = record_info.findtext("id")
    record_type = record_info.findtext("type/linkedRecordId")
    return RecordNode(record_id, record_type, url, root)


def find_child_urls(xml_root):
    urls = []
    for element in xml_root.findall(".//childReferences/childReference/ref/actionLinks/read/url"):
        urls.append((element.text or "").strip())
    print(f"  Found {len(urls)} child URLs: {urls}")
    return urls


def unwrap_and_clean_xml_for_create(xml_root: ET.Element) -> ET.Element:
    content = xml_root.find("data")[0]
    remove_unwanted_elements(content)
    return content


def remove_unwanted_elements(element: ET.Element):
    tags_to_remove = {"type", "createdBy", "tsCreated", "updated"}
    for child in list(element):
        if child.tag in tags_to_remove:
            element.remove(child)
        else:
            remove_unwanted_elements(child)


def to_xml_bytes(element):
    return b'<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(element, encoding="utf-8")


def find_top_level_children(xml_root):
    urls = []
    for tag in ["newMetadataId", "metadataId"]:
        element = xml_root.find(f".//{tag}/actionLinks/read/url")
        if element is not None:
            url = (element.text or "").strip()
            urls.append(url)
    print(f"  Top-level children found ({len(urls)}): {urls}")
    return urls


# API utilities ----------------------------------
def fetch_xml_from_api(url):
    print(f"Fetching: {url}")
    headers = {"Accept": "application/vnd.cora.record+xml"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def try_to_store_record(node, record_type_url: str, xml_bytes: bytes | Any) -> bool:
    try:
        headers = {
            "Authtoken": "189b5e3a-4a16-478c-b2ef-2c8a66de3e14",
            "Content-Type": "application/vnd.cora.recordgroup+xml",
            "Accept": "application/vnd.cora.record+xml", }

        response = requests.post(record_type_url, data=xml_bytes, headers=headers, timeout=10)
        print(f"  Response: ({response.status_code}) - {response.text}\n")
        if response.status_code not in (200, 201):
            TOTAL_ERRORS.append(f"Failed to save {node.new_record_id} ({response.status_code} - {response.text})")
            return False
        else:
            return True
    except requests.RequestException as e:
        print(f">>> Error saving {node.new_record_id}: {e}")
        TOTAL_ERRORS.append(f"Error saving {node.new_record_id}: {e}")
        return False


if __name__ == "__main__":
    main()
