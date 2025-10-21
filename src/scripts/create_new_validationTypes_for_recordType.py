import json
import xml.etree.ElementTree as ET
from collections import deque, defaultdict
from typing import Any

import requests

from common.arg_parser import create_argument_parser, common_arguments
from cora.context import CoraContext, Context

CTX: Context

# The recordType to process
RECORD_TYPE = "diva-output"

# Prefix for new validationTypes
TYPE_PREFIX = "__XYZ_"

# Ignored validation types
BLACKLIST_TYPES = ["diva-output", "tempContainerOutput"]

# Enable extensive logging of process
EXTENSIVE_LOGGING = False

# Global state
GLOBAL_NODE_MAP = {}
GLOBAL_ID_MAPPING = {}
GLOBAL_RECORD_INFO_CHILDREN = {}
TOTAL_PROCESSED_RECORDS = 0
TOTAL_UPDATES = 0
TOTAL_ERRORS = []
TOTAL_FETCHED = 0


# Representation of a record and its relationships ----------------------------------
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
    global CTX

    parser = create_argument_parser(
        description="Create new validationTypes with updated IDs and normalized values for a specific recordType.",
        arguments=common_arguments,
    )

    args = parser.parse_args()

    CTX = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    create_new_validation_types_for_record_type()


def create_new_validation_types_for_record_type():
    print("Creating new validationTypes for recordType:", RECORD_TYPE, "using prefix:", TYPE_PREFIX)
    CTX.log("Creating new validationTypes for recordType: " + RECORD_TYPE + " using prefix: " + TYPE_PREFIX)

    validation_types = get_validation_types_for_record_type()

    print("\n=== Building node map ===\n")
    CTX.log("=== Building node map ===")

    root_urls = [CTX.get_base_url() + "validationType/" + string for string in validation_types]
    for root_url in root_urls:
        build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)

    CTX.log(f"All records fetched: total unique records collected in node map: {len(GLOBAL_NODE_MAP)}")

    collect_record_info_children(GLOBAL_NODE_MAP)

    if EXTENSIVE_LOGGING: # pragma: no cover
        log_node_map_summary()

    print("\n\n=== Processing node map ===\n")
    CTX.log("=== Processing node map ===")

    process_node_map_bottom_up_and_store(GLOBAL_NODE_MAP, GLOBAL_ID_MAPPING)

    CTX.log("=== Script finished ===")
    log_results()

    print(f"\n=== Processing completed. Output logged to {CTX.get_log_file_path()} ===")


def collect_record_info_children(global_node_map):
    visited = set()
    parent_refs = defaultdict(set)

    record_info_roots = find_record_info_roots(global_node_map)

    queue = deque(record_info_roots)
    while queue:
        parent = queue.popleft()
        if parent.url in visited:
            continue
        visited.add(parent.url)

        if parent.url not in {root.url for root in record_info_roots}:
            GLOBAL_RECORD_INFO_CHILDREN[parent.url] = parent

        for child in parent.children:
            parent_refs[child.url].add(parent.url)
            if child.url not in visited:
                queue.append(child)


def find_record_info_roots(global_node_map) -> list[Any]:
    record_info_roots = [
        node for node in global_node_map.values()
        if record_info_group(node.xml_content)
    ]
    return record_info_roots


def log_results():
    CTX.log(f"  Total records fetched:   {TOTAL_FETCHED}")
    CTX.log(f"  Total records processed: {TOTAL_PROCESSED_RECORDS}")
    CTX.log(f"  Total records created:   {TOTAL_UPDATES}")

    if TOTAL_FETCHED != TOTAL_PROCESSED_RECORDS:
        CTX.log(f"\n>>> WARNING!! - Fetched {TOTAL_FETCHED} but only processed {TOTAL_PROCESSED_RECORDS} records.")

    if TOTAL_ERRORS:
        print("\nWarning! There were errors reported during processing, please check the log file for details.")
        CTX.log("=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            CTX.log(f" > {error}")
    else:
        print("\nNo errors reported.")
        CTX.log("No errors reported.")


def build_node_map_from_child_references(root_url, global_node_map):
    global TOTAL_FETCHED
    """
    - Top-level: newMetadataId + metadataId
    - Lower levels: only childReferences
    - Reuses previously fetched nodes stored in `node_map`.
    """
    if root_url in global_node_map:
        return global_node_map


    collect_nodes_from_root(root_url, global_node_map)
    link_parent_child_relationship(global_node_map)

    TOTAL_FETCHED = len(global_node_map)
    return global_node_map


def collect_nodes_from_root(root_url: str, global_node_map: dict[str, RecordNode]) -> None:
    queue = deque([root_url])
    while queue:
        url = queue.popleft()
        if url in global_node_map:
            continue

        xml_text = fetch_record_as_xml(url)
        node = parse_record_from_xml(xml_text, url)
        global_node_map[url] = node
        print(f"Fetching records... {len(global_node_map)}", end="\r", flush=True)

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

        print(f"Records processed: {TOTAL_PROCESSED_RECORDS} - Records created: {TOTAL_UPDATES}", end="\r", flush=True)

    print()
    check_for_unprocessed_nodes(global_node_map, processed)


def process_node(global_id_mapping, node):
    global TOTAL_PROCESSED_RECORDS, TOTAL_UPDATES, TOTAL_ERRORS

    try:
        TOTAL_PROCESSED_RECORDS += 1
        if process_and_possibly_save(node, global_id_mapping):
            TOTAL_UPDATES += 1

    except Exception as e:
        TOTAL_ERRORS.append(f"Error processing {node.record_id}: {e}")
        CTX.log(f"Error processing {node.record_id}: {e}")


def update_parent_dependencies(leaf_queue: deque[str], node, unprocessed_child_map: dict[str, int]):
    for parent in node.parents:
        if parent.url in unprocessed_child_map:
            unprocessed_child_map[parent.url] -= 1
            if unprocessed_child_map[parent.url] == 0:
                leaf_queue.append(parent.url)


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        CTX.log(f"\n>>> WARNING!! -  {len(unprocessed)} records were never processed:")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def process_and_possibly_save(node, global_id_mapping):
    old_id = node.record_id

    if skip_if_already_processed(node, global_id_mapping):
        return False

    updated = False
    if update_final_value_of_validation_type(node.xml_content):
        CTX.log(f"> Updated finalValue for {node.record_id} (validationType)")
        updated = True

    elif record_is_a_child_of_record_info(node):
        CTX.log(f"> Skipping {node.record_id} (record info child)")
        return False

    else:
        if normalize_regex_patterns(node.xml_content):
            CTX.log(f"> Normalized regex pattern(s) to '.+' in {old_id}")
            updated = True

        if normalize_child_reference_repeat(node.xml_content):
            CTX.log(f"> Normalized childReference(s) Min Max to '0-X' in {old_id}")
            updated = True

    child_renamed = any(child.record_id in global_id_mapping for child in node.children)

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
        CTX.log(f"Skipping already processed {old_id} -> {node.new_record_id}")
        return True
    return False


def prepare_and_try_to_save_record(node):
    record_type = node.xml_content.findtext(".//recordInfo/type/linkedRecordId")

    content_root = unwrap_and_clean_xml_for_create(node.xml_content)
    xml_bytes = to_xml_bytes(content_root)

    base_url = f"{CTX.get_base_url()}"
    record_type_url = f"{base_url}{record_type}"

    log_creation_summary(node, record_type, record_type_url, xml_bytes)

    return try_to_store_record(node, record_type_url, xml_bytes)


def log_creation_summary(node, record_type, record_type_url: str, xml_bytes: bytes | Any):
    CTX.log(f">>> Creating {node.new_record_id} ({record_type})...")
    CTX.log(f"  Endpoint: {record_type_url}")
    CTX.log("  Payload: " + xml_bytes.decode("utf-8"))


# XML utilities ----------------------------------
def record_info_group(xml_content):
    name_in_data = xml_content.findtext(".//metadata[@type='group']/nameInData")
    return name_in_data is not None and name_in_data == "recordInfo"


def record_is_a_child_of_record_info(node) -> bool:
    return node.url in GLOBAL_RECORD_INFO_CHILDREN


def update_final_value_of_validation_type(xml_content):
    name_in_data = xml_content.findtext(".//metadata[@type='recordLink']/nameInData")
    if name_in_data == "validationType":
        final_value = xml_content.find(".//metadata[@type='recordLink']/finalValue")
        if final_value is not None:
            current_value = final_value.text or ""
            final_value.text = TYPE_PREFIX + current_value
            return True
    return False


def normalize_regex_patterns(xml_root):
    updated = False
    if not record_info_group(xml_root):
        for tag in ("regex", "regEx", "pattern"):
            for element in xml_root.findall(f".//{tag}"):
                if element.text and element.text.strip() not in (None, ".+"):
                    element.text = ".+"
                    updated = True

    return updated


def normalize_child_reference_repeat(xml_root):
    updated = False
    if not record_info_group(xml_root):
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

    return urls


# API utilities ----------------------------------
def fetch_record_as_xml(url):
    headers = {"Authtoken": CTX.get_auth_token(), "Accept": "application/vnd.cora.record+xml"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def try_to_store_record(node, record_type_url: str, xml_bytes: bytes | Any) -> bool:
    try:
        headers = {
            "Authtoken": CTX.get_auth_token(),
            "Content-Type": "application/vnd.cora.recordgroup+xml",
            "Accept": "application/vnd.cora.record+xml", }

        response = requests.post(record_type_url, data=xml_bytes, headers=headers, timeout=10)
        CTX.log(f"  Response: ({response.status_code}) - {response.text}\n")
        if response.status_code not in (200, 201):
            TOTAL_ERRORS.append(f"Failed to save {node.new_record_id} ({response.status_code} - {response.text})")
            return False
        return True
    except requests.RequestException as e:
        CTX.log(f">>> Error saving {node.new_record_id}: {e}")
        TOTAL_ERRORS.append(f"Error saving {node.new_record_id}: {e}")
        return False


def get_validation_types_for_record_type():
    search_url = CTX.get_base_url() + "searchResult/validationTypeSearch"
    headers = {"Authtoken": CTX.get_auth_token(), "Accept": "application/vnd.cora.recordList+xml",
               "Content-Type": "application/vnd.cora.recordList+xml"}

    response = requests.get(search_url, params={"searchData": get_search_data()}, headers=headers)
    response.raise_for_status()
    response_body = ET.fromstring(response.text)

    return collect_validation_types_from_response(response_body)


def collect_validation_types_from_response(response_body: ET.Element) -> list[Any]:
    validation_types = []
    for element in response_body.findall(".//validationType/recordInfo/id"):
        if element.text is None or element.text.startswith("__") or element.text in BLACKLIST_TYPES:
            continue
        validation_types.append((element.text or "").strip())

    return validation_types


def get_search_data() -> bytes:
    search_data = {
        "name": "validationTypeSearch",
        "children": [
            {
                "name": "include",
                "children": [
                    {
                        "name": "includePart",
                        "children": [
                            {
                                "name": "validatesRecordTypeSearchTerm",
                                "value": f"recordType_{RECORD_TYPE}"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    return json.dumps(search_data).encode("utf-8")


def log_node_map_summary(): # pragma: no cover
    CTX.log("\n=== Node map Summary ===")
    for url, node in GLOBAL_NODE_MAP.items():
        CTX.log(f"{url} → {len(node.children)} children, {len(node.parents)} parents")


if __name__ == "__main__": # pragma: no cover
    main()
