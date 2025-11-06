from collections import deque, defaultdict
from typing import Any

from common import validation_type_utils as common_utils
from common.arg_parser import create_argument_parser
from cora.context import CoraContext, Context

CTX: Context

# The recordType to process
RECORD_TYPE = ""

# Prefix for new validationTypes
TYPE_PREFIX = ""

# Data divider to set for new validationType
DATA_DIVIDER = ""

# Existing prefiex validation types
EXISTING_VALIDATION_TYPES_WITH_PREFIX = []

# Ignored validation types
BLACKLIST_TYPES = ["diva-output", "tempContainerOutput"]

# DRY RUN MODE
DRY_RUN = True

# Enable extensive logging of process
EXTENSIVE_LOGGING = True

# Global state
GLOBAL_NODE_MAP = {}
GLOBAL_ID_MAPPING = {}
GLOBAL_RECORD_INFO_CHILDREN = {}
TOTAL_PROCESSED_RECORDS = 0
TOTAL_UPDATES = 0
TOTAL_CREATED = 0
TOTAL_ERRORS = []
TOTAL_FETCHED = 0


def main():
    global CTX, DRY_RUN, TYPE_PREFIX, RECORD_TYPE, DATA_DIVIDER

    parser = create_argument_parser(
        description="Create new validationTypes with updated IDs and normalized values for a specific recordType.",
        arguments=common_utils.create_validation_type_args
    )

    args = parser.parse_args()

    DRY_RUN = not args.apply
    TYPE_PREFIX = args.prefix
    RECORD_TYPE = args.recordtype
    DATA_DIVIDER = args.datadivider

    CTX = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )

    common_utils.init(CTX, TYPE_PREFIX, RECORD_TYPE, BLACKLIST_TYPES)

    if DRY_RUN:
        common_utils.log(
            "[SCRIPT IN DRY RUN MODE] - No changes will be applied to the system, use --apply to apply changes")

    create_new_validation_types_for_record_type()


def create_new_validation_types_for_record_type():
    global TOTAL_FETCHED
    common_utils.log("Creating new validationTypes for recordType: " + RECORD_TYPE + " using prefix: " + TYPE_PREFIX)

    validation_types = get_validation_types_to_process()

    common_utils.log("=== Building node map ===")

    root_urls = common_utils.get_root_urls_for_validation_types(validation_types)
    for root_url in root_urls:
        common_utils.build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)
        TOTAL_FETCHED = len(GLOBAL_NODE_MAP)

    CTX.log(f"All records fetched: total unique records collected in node map: {len(GLOBAL_NODE_MAP)}")

    collect_record_info_children(GLOBAL_NODE_MAP)

    common_utils.log("=== Processing node map ===")

    process_node_map_bottom_up_and_store(GLOBAL_NODE_MAP, GLOBAL_ID_MAPPING)

    common_utils.log("=== Script finished ===")
    log_results()

    print(f"\n=== Output logged to {CTX.get_log_file_path()} ===")


def get_validation_types_to_process() -> list[Any]:
    global EXISTING_VALIDATION_TYPES_WITH_PREFIX

    EXISTING_VALIDATION_TYPES_WITH_PREFIX = common_utils.get_ids_for_record_type_matching_prefix("validationType")
    if EXISTING_VALIDATION_TYPES_WITH_PREFIX:
        common_utils.log(
            f"Found existing validation types that use prefix '{TYPE_PREFIX}', will possibly update these and create needed new ones.")
        return EXISTING_VALIDATION_TYPES_WITH_PREFIX

    common_utils.log(f"Could not find any existing validation types with prefix '{TYPE_PREFIX}', will create new ones.")
    return common_utils.get_validation_types_for_record_type()


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
        if common_utils.record_info_group(node.xml_content)
    ]
    return record_info_roots


def log_results():  # pragma: no cover
    common_utils.log(f"  Total records fetched:   {TOTAL_FETCHED}")
    common_utils.log(f"  Total records processed: {TOTAL_PROCESSED_RECORDS}")
    common_utils.log(f"  Total records created:   {TOTAL_CREATED}")
    common_utils.log(f"  Total records updated:   {TOTAL_UPDATES}")

    if TOTAL_FETCHED != TOTAL_PROCESSED_RECORDS:
        common_utils.log(
            f"\n>>> WARNING!! - Fetched {TOTAL_FETCHED} but only processed {TOTAL_PROCESSED_RECORDS} records.")

    if TOTAL_ERRORS:
        print("\nWarning! There were errors reported during processing, please check the log file for details.")
        CTX.log("=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            CTX.log(f" > {error}")
    else:
        common_utils.log("No errors reported.")


def process_node_map_bottom_up_and_store(global_node_map, global_id_mapping):
    """
    Kahn's algorithm for topological sorting.
    Processes nodes only after all their children have been processed.
    """

    # Build map and leaf queue of records to process
    unprocessed_child_map = {}
    leaf_queue = deque()
    for url, node in global_node_map.items():
        cnt = len(node.children)
        unprocessed_child_map[url] = cnt
        if cnt == 0:
            leaf_queue.append(url)

    processed: set[str] = set()

    while leaf_queue:
        child_reference_url = leaf_queue.popleft()
        node = global_node_map[child_reference_url]

        process_node(global_id_mapping, node)
        processed.add(child_reference_url)
        for parent in node.parents:
            if parent.url in unprocessed_child_map:
                unprocessed_child_map[parent.url] -= 1
                if unprocessed_child_map[parent.url] == 0:
                    leaf_queue.append(parent.url)

        print(
            f"Records processed: {len(processed)} - Records created: {TOTAL_CREATED} - Records updated: {TOTAL_UPDATES}",
            end="\r", flush=True)

    print()
    check_for_unprocessed_nodes(global_node_map, processed)


def process_node(global_id_mapping, node):
    global TOTAL_PROCESSED_RECORDS, TOTAL_UPDATES, TOTAL_ERRORS, EXISTING_VALIDATION_TYPES_WITH_PREFIX, TOTAL_CREATED

    try:
        TOTAL_PROCESSED_RECORDS += 1
        if node.record_id in EXISTING_VALIDATION_TYPES_WITH_PREFIX:
            if process_and_possibly_update(node, global_id_mapping):
                TOTAL_UPDATES += 1

        else:
            if process_and_possibly_create(node, global_id_mapping):
                TOTAL_CREATED += 1

    except Exception as e:
        TOTAL_ERRORS.append(f"Error processing {node.record_id}: {e}")
        CTX.log(f"Error processing {node.record_id}: {e}")


def process_and_possibly_update(node, global_id_mapping):
    if DRY_RUN:
        CTX.log(f"  Dry run mode - not updating {node.new_record_id}\n")
        return True

    original_id = node.record_id
    if is_already_processed(node.record_id, global_id_mapping):
        node.new_record_id = global_id_mapping[original_id]
        return False

    if not common_utils.link_dependency_to_top_groups(node.xml_content):
        CTX.log(f"Top group dependencies was already set to use prefixes, skipping update of '{node.record_id}'...")
        return False
    common_utils.remove_action_links(node.xml_content)
    common_utils.update_child_references(node.xml_content, global_id_mapping)

    return common_utils.try_to_update_record(node, TOTAL_ERRORS)


def process_and_possibly_create(node, global_id_mapping):
    original_id = node.record_id

    if is_already_processed(node.record_id, global_id_mapping):
        node.new_record_id = global_id_mapping[original_id]
        return False

    updated = False
    common_utils.possibly_set_to_not_create_presentations(node)

    if common_utils.update_final_value_of_validation_type(node.xml_content):
        CTX.log(f"> Updated finalValue for {original_id} (validationType)")
        updated = True

    elif common_utils.record_is_a_child_of_record_info(node, GLOBAL_RECORD_INFO_CHILDREN):
        CTX.log(f"> Skipping {original_id} (record info child)")
        return False

    else:
        updated = common_utils.possibly_update_data_of_non_record_info_child(node, original_id, updated)

    child_renamed = any(child.record_id in global_id_mapping for child in node.children)

    if not (updated or child_renamed):
        common_utils.update_child_references(node.xml_content, global_id_mapping)
        return False

    new_id = common_utils.create_new_id_and_update_mapping(global_id_mapping, node)
    common_utils.update_record_id_in_xml(node.xml_content, new_id)
    common_utils.update_child_references(node.xml_content, global_id_mapping)
    common_utils.remove_action_links(node.xml_content)

    if common_utils.update_data_divider(node.xml_content, DATA_DIVIDER):
        CTX.log(f"> Updated data divider of {original_id}")

    return prepare_and_try_to_save_record(node)


# def update_parent_dependencies(leaf_queue: deque[str], node, unprocessed_child_map: dict[str, int]):
#    for parent in node.parents:
#        if parent.url in unprocessed_child_map:
#            unprocessed_child_map[parent.url] -= 1
#            if unprocessed_child_map[parent.url] == 0:
#                leaf_queue.append(parent.url)


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        CTX.log(f"\n>>> WARNING!! -  {len(unprocessed)} records were never processed:")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def is_already_processed(node_id: str, global_id_mapping: dict) -> bool:
    return node_id in global_id_mapping


def prepare_and_try_to_save_record(node):
    if DRY_RUN:
        CTX.log(f"  Dry run mode - not saving {node.new_record_id}\n")
        return True

    content_root = common_utils.unwrap_and_clean_xml_for_create(node.xml_content)

    return common_utils.try_to_create_record(node, content_root, TOTAL_ERRORS)


if __name__ == "__main__":  # pragma: no cover
    main()
