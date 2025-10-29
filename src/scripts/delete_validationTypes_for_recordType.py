import json
import xml.etree.ElementTree as ET
from collections import deque
from typing import Any

import requests

from common.arg_parser import create_argument_parser, ArgumentConfig
from cora.context import CoraContext, Context

CTX: Context

# Prefix for new validationTypes
TYPE_PREFIX = ""

# Ignored validation types
BLACKLIST_TYPES = ["diva-output", "tempContainerOutput"]

# DRY RUN MODE
DRY_RUN = True

# Global state
GLOBAL_NODE_MAP = {}
GLOBAL_ID_MAPPING = {}
GLOBAL_RECORD_INFO_CHILDREN = {}
TOTAL_PROCESSED_RECORDS = 0
TOTAL_RECORD_DELETIONS = 0
TOTAL_PRESENTATION_DELETIONS = 0
TOTAL_ERRORS = []

script_arguments: dict[str, ArgumentConfig] = {
    "--system": {
        "help": "Cora system to connect to (e.g., 'preview', 'production')",
        "type": str,
        "default": "minikube",
    },
    "--login-id": {
        "default": "divaAdmin@cora.epc.ub.uu.se",
        "help": "Login ID for authentication",
    },
    "--app-token": {
        "default": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
        "help": "Application token for authentication",
    },
    "--apply": {
        "help": "Apply changes to the Cora system (dry run if not present)",
        "action": "store_true",
    },
    "--workers": {
        "help": "Number of worker threads for processing",
        "type": int,
        "default": 16,
    },
    "--prefix": {
        "help": "Which prefix to use for deletions (only records and presentations using this ID-prefix will be deleted",
        "type": str,
        "required": True,
    },
}


# Representation of a record and its relationships ----------------------------------
class RecordNode:
    def __init__(self, record_id, record_type, url, xml_content):
        self.record_id: str = record_id
        self.record_type = record_type
        self.url = url
        self.xml_content = xml_content
        self.child_urls = []
        self.children = []
        self.parents = []
        self.new_record_id = None


def main():
    global CTX, DRY_RUN, TYPE_PREFIX

    parser = create_argument_parser(
        description="Delete presentations and metadata for all records matching the supplied prefix.",
        arguments=script_arguments
    )

    args = parser.parse_args()

    DRY_RUN = not args.apply
    TYPE_PREFIX = args.prefix

    CTX = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    if DRY_RUN:
        log(">>> [SCRIPT IN DRY RUN MODE] - No changes will be applied to the system, use --apply to apply changes")

    delete_records_with_prefix()


def delete_records_with_prefix():
    log("Deleting all records and presentations that use prefix: " + TYPE_PREFIX)

    log("=== Deleting all presentations ===")
    try_to_delete_presentations()
    print()

    log("=== Building node map ===")
    validation_types = get_validation_types_for_record_type()
    if not validation_types:
        log("No validationTypes found to delete...")
    else:
        print("\n...artistic pause...")
        root_urls = get_root_urls_for_validation_types(validation_types)
        for root_url in root_urls:
            build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)

    print()
    log("=== Deleting records ===")

    if not GLOBAL_NODE_MAP:
        log("There is nothing to delete...")
    else:
        print("\n~ Heavy metal riff playing ~")
        process_node_map_and_delete_records(GLOBAL_NODE_MAP)

    log("=== Script finished ===")
    log_results()

    print(f"\n=== Processing completed. Output logged to {CTX.get_log_file_path()} ===")


def try_to_delete_presentations():
    global TOTAL_PRESENTATION_DELETIONS
    response = get_search_result_for_type("presentation")
    delete_urls = deque(collect_presentations_from_response(response))
    if not delete_urls:
        log("No presentations found to delete...")
        return

    print("\n~ Heavy metal riff playing ~")
    total = len(delete_urls)
    retries: dict[str, int] = {}
    while delete_urls:
        url = delete_urls.popleft()
        if DRY_RUN:
            TOTAL_PRESENTATION_DELETIONS += 1
            print(f"Presentations annihilated from existance: {TOTAL_PRESENTATION_DELETIONS} / {total}", end="\r", flush=True)
        else:
            deleted = try_to_delete_record(url)
            if deleted:
                TOTAL_PRESENTATION_DELETIONS += 1
                print(f"Presentations annihilated from existance: {TOTAL_PRESENTATION_DELETIONS} / {total}", end="\r", flush=True)
            else:
                if retries.get(url, 0) >= 5:
                    TOTAL_ERRORS.append("Failed to delete " + url + " after 5 retries!")
                else:
                    CTX.log(f"   - Failed to delete record. Will retry... number of retries so far: {retries.get(url, 0)} / 5\n")
                    delete_urls.append(url)
                    retries[url] = retries.get(url, 0) + 1


def get_validation_types_for_record_type():
    response_body = get_search_result_for_type("validationType")
    return collect_validation_types_from_response(response_body)


def get_root_urls_for_validation_types(validation_types: list[str]) -> list[str]:
    return [CTX.get_base_url() + "validationType/" + string for string in validation_types]


def build_node_map_from_child_references(root_url, global_node_map):
    """
    - Top-level: newMetadataId + metadataId
    - Lower levels: only childReferences
    """
    if root_url in global_node_map:
        return global_node_map

    collect_nodes_from_root(root_url, global_node_map)
    link_parent_child_relationship(global_node_map)

    return global_node_map


def process_node_map_and_delete_records(global_node_map):
    global TOTAL_RECORD_DELETIONS
    """
    A node is deleted only when no other node references it
    """

    remaining_parent_count = {
        url: len(node.parents)
        for url, node in global_node_map.items()
    }

    deletion_queue = deque([url for url, count in remaining_parent_count.items() if count == 0])
    processed: set[str] = set()

    while deletion_queue:
        url = deletion_queue.popleft()
        node = global_node_map[url]

        if prepare_url_and_possibly_delete(node):
            TOTAL_RECORD_DELETIONS += 1
            print(f"Records purged from this world: {TOTAL_RECORD_DELETIONS} / {len(global_node_map)}", end="\r", flush=True)

        processed.add(url)

        for child in node.children:
            child_url = child.url
            if child_url in remaining_parent_count:
                remaining_parent_count[child_url] -= 1

                if remaining_parent_count[child_url] == 0:
                    deletion_queue.append(child_url)

    print()
    check_for_unprocessed_nodes(global_node_map, processed)


def log_results(): # pragma: no cover
    if DRY_RUN:
        log("[ Script ran in dry run mode ]")

    log(f"  Total presentations deleted: {TOTAL_PRESENTATION_DELETIONS}")
    log(f"  Total records deleted: {TOTAL_RECORD_DELETIONS}")

    if TOTAL_ERRORS:
        print("\nWarning! There were errors reported during processing, please check the log file for details.")
        CTX.log("=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            CTX.log(f" > {error}")
    else:
        log("  No errors reported.")


def collect_nodes_from_root(root_url: str, global_node_map: dict[str, RecordNode]) -> None:
    queue = deque([root_url])
    while queue:
        url = queue.popleft()
        if url in global_node_map:
            continue

        xml_text = fetch_record_as_xml(url)
        node = parse_record_from_xml(xml_text, url)
        if node.record_id.startswith(TYPE_PREFIX):
            global_node_map[url] = node

        print(f"Fetching validation types and their children: {len(global_node_map)}", end="\r", flush=True)

        child_urls = collect_child_urls(node, root_url, url)
        for child_url in child_urls:
            if child_url not in global_node_map:
                queue.append(child_url)


def collect_child_urls(node: RecordNode, root_url, url) -> list[str]:
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


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        log("Some records were not processed (and probably not deleted), check log for more info...")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def prepare_url_and_possibly_delete(node):
    if not f"{node.record_id}".startswith(TYPE_PREFIX):
        return False

    base_url = f"{CTX.get_base_url()}"
    record_type_url = f"{base_url}{node.record_type}/{node.record_id}"

    if DRY_RUN:
        return True
    return try_to_delete_record(record_type_url)


# XML utilities ----------------------------------
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


def find_top_level_children(xml_root):
    urls = []
    for tag in ["newMetadataId", "metadataId"]:
        element = xml_root.find(f".//{tag}/actionLinks/read/url")
        if element is not None:
            url = (element.text or "").strip()
            urls.append(url)

    return urls


def collect_presentations_from_response(response_body: ET.Element) -> set[str]:
    delete_urls = set()
    for element in response_body.findall(".//presentation/recordInfo/id"):
        if TYPE_PREFIX in element.text:
            delete_urls.add((CTX.get_base_url() + "presentation/" + element.text or "").strip())
    return delete_urls


def collect_validation_types_from_response(response_body: ET.Element) -> list[str]:
    validation_types = []
    for element in response_body.findall(".//validationType/recordInfo/id"):
        if element.text is None or element.text in BLACKLIST_TYPES:
            continue

        if TYPE_PREFIX in element.text:
            validation_types.append((element.text or "").strip())

    return validation_types


# API utilities ----------------------------------
def fetch_record_as_xml(url):
    headers = {"Authtoken": CTX.get_auth_token(), "Accept": "application/vnd.cora.record+xml"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def try_to_delete_record(record_type_url: str | Any) -> bool:
    try:
        headers = {
            "Authtoken": CTX.get_auth_token(),
            "Accept": "*/*", }

        if TYPE_PREFIX not in record_type_url:
            TOTAL_ERRORS.append(
                f"Tried to delete a record that probably wasn't supposed to be deleted... {record_type_url}")
            return False

        response = requests.delete(record_type_url, headers=headers, timeout=10)
        CTX.log(f"  URL: {record_type_url}")
        CTX.log(f"  Response: ({response.status_code}) - {response.text}")
        if response.status_code not in (200, 201):
            return False
        return True
    except requests.RequestException as e:
        TOTAL_ERRORS.append(f"Error saving {record_type_url}: {e}")
        return False


def get_search_result_for_type(type_name: str) -> ET.Element:
    search_url = CTX.get_base_url() + f"searchResult/{type_name}Search"
    headers = {"Authtoken": CTX.get_auth_token(), "Accept": "application/vnd.cora.recordList+xml",
               "Content-Type": "application/vnd.cora.recordList+xml"}

    response = requests.get(search_url, params={"searchData": get_search_data(type_name)}, headers=headers)
    response.raise_for_status()
    response_body = ET.fromstring(response.text)
    return response_body


def get_search_data(type_name: str) -> bytes:
    search_data = {
        "name": f"{type_name}Search",
        "children": [
            {
                "name": "include",
                "children": [
                    {
                        "name": "includePart",
                        "children": [
                            {
                                "name": "recordIdSearchTerm",
                                "value": f"{TYPE_PREFIX}*"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "rows",
                "value": "1000"
            }
        ]
    }

    return json.dumps(search_data).encode("utf-8")


def log(text: str):
    print(f"\n{text}")
    CTX.log(text)


if __name__ == "__main__":  # pragma: no cover
    main()
