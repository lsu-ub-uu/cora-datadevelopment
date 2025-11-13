import json
import xml.etree.ElementTree as ET
from collections import deque
from typing import Any
from xml.etree.ElementTree import Element

import requests

from common.arg_parser import ArgumentConfig
from cora.context import CoraContext

_ctx: CoraContext
_type_prefix: str
_record_type: str
_black_list: list


def init(ctx: CoraContext, type_prefix: str, record_type: str, black_list: list):
    global _ctx, _type_prefix, _record_type, _black_list
    _ctx = ctx
    _type_prefix = type_prefix
    _record_type = record_type
    _black_list = black_list


create_validation_type_args: dict[str, ArgumentConfig] = {
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
    "--datadivider": {
        "help": "The data divider to set for the created records (e.g, 'diva', 'cora')",
        "type": str,
        "default": "diva",
    },
    "--recordtype": {
        "help": "Which recordType to create the new validationTypes for",
        "type": str,
        "required": True,
    },
    "--prefix": {
        "help": "Which prefix to add to the new validationType IDs",
        "type": str,
        "required": True,
    },
}

delete_validation_type_args: dict[str, ArgumentConfig] = {
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
    def __init__(self, record_id: str, record_type: str, url: str, xml_content: Element):
        self.record_id = record_id
        self.record_type = record_type
        self.url = url
        self.xml_content = xml_content
        self.child_urls = []
        self.children = []
        self.parents = []
        self.new_record_id = None


def get_root_urls_for_validation_types(validation_types: list[str]) -> list[str]:
    return [_ctx.get_base_url() + "validationType/" + string for string in validation_types]


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


def collect_nodes_from_root(root_url: str, global_node_map: dict[str, RecordNode]) -> None:
    queue = deque([root_url])
    while queue:
        url = queue.popleft()
        if url in global_node_map:
            continue

        xml_text = fetch_record_as_xml(url)
        node = parse_record_from_xml(xml_text, url)
        global_node_map[url] = node
        print(f"Fetching records: {len(global_node_map)}", end="\r", flush=True)

        child_urls = collect_child_urls(node, root_url, url)

        for child_url in child_urls:
            if child_url not in global_node_map:
                queue.append(child_url)


def link_parent_child_relationship(global_node_map: dict[Any, Any]):
    for node in global_node_map.values():
        for child_url in node.child_urls:
            if child_url in global_node_map:
                node.children.append(global_node_map[child_url])
                global_node_map[child_url].parents.append(node)


def record_info_group(xml_content):
    name_in_data = xml_content.findtext(".//metadata[@type='group']/nameInData")
    return name_in_data is not None and name_in_data == "recordInfo"


def record_is_a_child_of_record_info(node, global_record_info_children: dict[str, Any]) -> bool:
    return node.url in global_record_info_children


def update_final_value_of_validation_type(xml_content):
    name_in_data = xml_content.findtext(".//metadata[@type='recordLink']/nameInData")
    if name_in_data == "validationType":
        final_value = xml_content.find(".//metadata[@type='recordLink']/finalValue")
        if final_value is not None:
            current_value = final_value.text or ""
            final_value.text = _type_prefix + current_value
            return True
    return False


def possibly_update_data_of_non_record_info_child(node, record_info_groups: set, updated: bool) -> bool:
    if set_data_quality_to_classic(node.xml_content):
        _ctx.log(f"> Set data quality to classic in {node.record_id}")
        updated = True

    if normalize_regex_patterns(node.xml_content):
        _ctx.log(f"> Normalized regex pattern(s) to '.+' in {node.record_id}")
        updated = True

    if normalize_child_reference_repeat(node.xml_content, record_info_groups):
        _ctx.log(f"> Normalized childReference(s) Min Max to '0-X' in {node.record_id}")
        updated = True
    return updated


def is_record_info_child_ref(child_reference: Element, record_info_groups: set) -> bool:
    linked_record_id = child_reference.find(".//ref/linkedRecordId")
    if linked_record_id is not None and linked_record_id.text in record_info_groups:
        _ctx.log(f"Skipped normalizing '{linked_record_id.text}' due to being a record info group")
        return True
    return False


def set_data_quality_to_classic(xml_content):
    name_in_data = xml_content.findtext(".//metadata/nameInData")
    if name_in_data == "dataQuality":
        final_value = xml_content.find(".//metadata/finalValue")
        if final_value is not None:
            final_value.text = "classic"
            return True
    return False


def normalize_regex_patterns(xml_root):
    updated = False
    if not record_info_group(xml_root):
        for tag in ("regex", "regEx"):
            for element in xml_root.findall(f".//{tag}"):
                if element.text and element.text.strip() not in (None, ".+"):
                    element.text = ".+"
                    updated = True

    return updated


def normalize_child_reference_repeat(xml_root: Element, record_info_groups: set):
    updated = False
    if not record_info_group(xml_root):
        for child_reference in xml_root.findall(".//childReferences/childReference"):
            if is_record_info_child_ref(child_reference, record_info_groups):
                continue

            repeat_min_element = child_reference.find("repeatMin")
            repeat_max_element = child_reference.find("repeatMax")

            if repeat_min_element is not None and repeat_min_element.text != "0":
                repeat_min_element.text = "0"
                updated = True
            if repeat_max_element is not None and repeat_max_element.text != "X":
                repeat_max_element.text = "X"
                updated = True
    return updated


def update_data_divider(xml_root: Element, divider: str):
    updated = False
    data_divider = xml_root.find(".//recordInfo/dataDivider/linkedRecordId")
    if data_divider is not None:
        current_value = (data_divider.text or "").strip()
        if current_value != divider:
            data_divider.text = divider
            updated = True

    return updated


def update_child_references(xml_root, id_mapping):
    for element in xml_root.findall(".//linkedRecordId"):
        original_id = (element.text or "").strip()
        if original_id in id_mapping:
            element.text = str(id_mapping[original_id])


def create_new_id_and_update_mapping(global_id_mapping, node) -> str:
    new_id = node.record_id if node.record_id.startswith(_type_prefix) else f"{_type_prefix}{node.record_id}"
    node.new_record_id = new_id
    global_id_mapping[node.record_id] = new_id
    return new_id


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


def fetch_record_as_xml(url: str):
    headers = {"Authtoken": _ctx.get_auth_token(), "Accept": "application/vnd.cora.record+xml"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def unwrap_and_clean_xml_for_create(xml_root: ET.Element) -> ET.Element:
    content = xml_root.find("data")[0]
    remove_unwanted_elements_for_creation(content)
    return content


def remove_unwanted_elements_for_creation(element: ET.Element):
    tags_to_remove = {"type", "createdBy", "tsCreated", "updated"}
    for child in list(element):
        if child.tag in tags_to_remove:
            element.remove(child)
        else:
            remove_unwanted_elements_for_creation(child)


def to_xml_bytes(element):
    return b'<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(element, encoding="utf-8")


def collect_child_urls(node: RecordNode, root_url, url) -> list[Any]:
    if url == root_url:
        child_urls = find_top_level_children(node.xml_content)
    else:
        child_urls = find_child_urls(node.xml_content)

    node.child_urls = child_urls
    return child_urls


def find_top_level_children(xml_root):
    urls = []
    for tag in ["newMetadataId", "metadataId"]:
        element = xml_root.find(f".//{tag}/actionLinks/read/url")
        if element is not None:
            url = (element.text or "").strip()
            urls.append(url)

    return urls


def find_child_urls(xml_root):
    urls = []
    for element in xml_root.findall(".//childReferences/childReference/ref/actionLinks/read/url"):
        urls.append((element.text or "").strip())

    return urls


def get_validation_type_search_data_for_record_type(record_type: str) -> bytes:
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
                                "value": f"recordType_{record_type}"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    return json.dumps(search_data).encode("utf-8")


def get_record_id_search_data_for_prefix_using_record_type(type_name: str) -> bytes:
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
                                "value": f"{_type_prefix}*"
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


def get_validation_types_for_record_type():
    search_data = get_validation_type_search_data_for_record_type(_record_type)
    response_body = get_validation_types_using_search_data("validationType", search_data)

    return collect_ids_from_response("validationType", response_body)


def get_ids_for_record_type_matching_prefix(record_type: str):
    search_data = get_record_id_search_data_for_prefix_using_record_type(record_type)
    response_body = get_validation_types_using_search_data(record_type, search_data)

    return collect_ids_from_response_matching_prefix(record_type, response_body)


def get_validation_types_using_search_data(record_type: str, search_data: bytes):
    search_url = _ctx.get_base_url() + f"searchResult/{record_type}Search"
    headers = {"Authtoken": _ctx.get_auth_token(),
               "Accept": "application/vnd.cora.recordList+xml",
               "Content-Type": "application/vnd.cora.recordList+xml"}

    response = requests.get(search_url, params={"searchData": search_data}, headers=headers)
    response.raise_for_status()
    response_body = ET.fromstring(response.text)

    return response_body


def collect_ids_from_response_matching_prefix(record_type: str, response_body: ET.Element) -> list[Any]:
    ids = []
    for element in response_body.findall(f".//{record_type}/recordInfo/id"):
        record_id = element.text
        if record_id is None or record_id in _black_list:
            continue

        if element.text.startswith(_type_prefix):
            ids.append((element.text or "").strip())

    return ids


def collect_ids_from_response(record_type: str, response_body: ET.Element) -> list[Any]:
    ids = []
    for element in response_body.findall(f".//{record_type}/recordInfo/id"):
        record_id = element.text
        if record_id is None or record_id in _black_list:
            continue

        ids.append((element.text or "").strip())

    return ids


def break_dependency_to_top_groups(xml_content):
    updated = False
    updated |= remove_prefix_from_value_of_xpath_using_find(xml_content, ".//newMetadataId/linkedRecordId")
    updated |= remove_prefix_from_value_of_xpath_using_find(xml_content, ".//metadataId/linkedRecordId")

    return updated


def remove_prefix_from_value_of_xpath_using_find(xml_content, path: str) -> bool:
    metadata_id = xml_content.find(path)
    if metadata_id is not None:
        current_id = metadata_id.text or ""
        metadata_id.text = current_id.removeprefix(_type_prefix)
        return True
    return False


def link_dependency_to_top_groups(xml_content):
    updated = False
    updated |= update_prefix_of_value_of_xpath_using_find(xml_content, ".//newMetadataId/linkedRecordId")
    updated |= update_prefix_of_value_of_xpath_using_find(xml_content, ".//metadataId/linkedRecordId")
    return updated


def update_prefix_of_value_of_xpath_using_find(xml_content, path: str) -> bool:
    metadata_id = xml_content.find(path)
    if metadata_id is not None:
        current_id = metadata_id.text or ""
        if not current_id.startswith(_type_prefix):
            metadata_id.text = _type_prefix + current_id
            return True
    return False


def possibly_set_to_not_create_presentations(node):
    metadata = node.xml_content.find(".//metadata[@type='group']")
    if metadata is None:
        return

    element = metadata.find('excludePGroupCreation')
    if element is None:
        element = ET.Element('excludePGroupCreation')
        element.text = 'true'
        metadata.append(element)


def log(text: str):  # pragma: no cover
    print(f"\n{text}")
    _ctx.log(text)


def log_creation_summary(node, record_type_url: str, xml_bytes: bytes | Any):  # pragma: no cover
    _ctx.log(f">>> POST {node.new_record_id} ({node.record_type})...")
    _ctx.log(f"  Endpoint: {record_type_url}")
    _ctx.log("  Payload: " + xml_bytes.decode("utf-8"))


# ---- API

def try_to_create_record(node, content_root, errors: list) -> bool:
    xml_bytes = to_xml_bytes(content_root)
    create_url = f"{_ctx.get_base_url()}{node.record_type}"

    return try_to_post_record(node, xml_bytes, create_url, errors)


def try_to_update_record(node, errors: list) -> bool:
    xml_bytes = to_xml_bytes(node.xml_content.find("data")[0])
    update_url = f"{_ctx.get_base_url()}{node.record_type}/{node.record_id}"

    return try_to_post_record(node, xml_bytes, update_url, errors)


def prepare_and_delete_record(node: RecordNode, errors: list):
    delete_url = f"{_ctx.get_base_url()}{node.record_type}/{node.record_id}"
    return try_to_delete_record(delete_url, errors)


def try_to_post_record(node: RecordNode, xml_bytes: bytes, url: str, errors: list) -> bool:
    log_creation_summary(node, url, xml_bytes)
    headers = {
        "Authtoken": _ctx.get_auth_token(),
        "Content-Type": "application/vnd.cora.recordgroup+xml",
        "Accept": "application/vnd.cora.record+xml", }

    try:
        response = requests.post(url, data=xml_bytes, headers=headers, timeout=10)
        _ctx.log(f"  Response: ({response.status_code}) - {response.text}\n")
        if response.status_code not in (200, 201):
            errors.append(f"Failed to save {node.new_record_id} ({response.status_code} - {response.text})")
            return False

        return True
    except requests.RequestException as e:
        _ctx.log(f">>> Error saving {node.new_record_id}: {e}")
        errors.append(f"Error saving {node.new_record_id}: {e}")
        return False


def try_to_delete_record(record_type_url: str, errors: list) -> bool:
    _ctx.log(f"DELETE: {record_type_url}")
    try:
        headers = {
            "Authtoken": _ctx.get_auth_token(),
            "Accept": "*/*", }

        if _type_prefix not in record_type_url:
            errors.append(
                f"Tried to delete a record that probably wasn't supposed to be deleted... {record_type_url}")
            return False

        response = requests.delete(record_type_url, headers=headers, timeout=10)
        _ctx.log(f"  Response: ({response.status_code}) - {response.text}")
        if response.status_code not in (200, 201):
            errors.append(f"Failed to delete record: {record_type_url}")
            return False
        return True
    except requests.RequestException as e:
        errors.append(f"Error saving {record_type_url}: {e}")
        return False
