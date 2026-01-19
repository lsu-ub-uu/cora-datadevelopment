from collections import deque

from tqdm import tqdm

from common import validation_type_utils as utils
from common.arg_parser import create_argument_parser
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
VALIDATION_TYPE_TEXTS = set()
TOTAL_PREFIX_MATCHES = 0
TOTAL_PROCESSED_RECORDS = 0
TOTAL_RECORD_DELETIONS = 0
TOTAL_RECORD_UPDATES = 0
TOTAL_ERRORS = []


def main():  # pragma: no cover
    global CTX, DRY_RUN, TYPE_PREFIX

    parser = create_argument_parser(
        description="Delete presentations and metadata for all records matching the supplied prefix.",
        arguments=utils.delete_validation_type_args
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

    utils.init(CTX, TYPE_PREFIX, "diva-output", BLACKLIST_TYPES)

    utils.log(start_delete_script_printout(args.system))

    if DRY_RUN:
        utils.log(
            ">>> [SCRIPT IN DRY RUN MODE] - No changes will be applied to the system, use --apply to apply changes")

    delete_records_with_prefix()


def start_delete_script_printout(system: str):  # pragma: no cover
    return f'''=== Deleting new validation types ===
 • System: {system}
 • System base url: {CTX.get_base_url()}
 • Prefix: {TYPE_PREFIX}'''


def delete_records_with_prefix():
    utils.log("=== Deleting presentations ===")
    delete_records_of_type_matching_prefix("presentation")

    utils.log("=== Building node map ===")
    build_node_map()

    utils.log("=== Deleting records ===")
    delete_records()
    delete_records_of_type_matching_prefix("text")

    utils.log("=== Script finished ===")
    log_results()

    print(f"\n=== Processing completed. Output logged to {CTX.get_log_file_path()} ===")


def delete_records_of_type_matching_prefix(type: str):
    global TOTAL_RECORD_DELETIONS
    record_ids = utils.get_ids_for_record_type_matching_prefix(type)
    delete_urls = deque(construct_delete_urls_from_ids(record_ids, type))

    if not delete_urls:
        utils.log("No " + type + "s found to delete...")
        return

    total = len(delete_urls)
    retries: dict[str, int] = {}
    progress = tqdm(total=total, desc="Deleting " + type + "s", bar_format="{l_bar}{bar:30}{r_bar}")
    while delete_urls:
        url = delete_urls.popleft()

        if DRY_RUN:
            progress.update(1)
        else:
            deleted = utils.try_to_delete_record(url, TOTAL_ERRORS)
            if deleted:
                progress.update(1)
                TOTAL_RECORD_DELETIONS += 1
            else:
                if retries.get(url, 0) >= 5:
                    TOTAL_ERRORS.append("Failed to delete " + url + " after 5 retries!")
                else:
                    CTX.log(
                        f"   - Failed to delete record. Will retry... number of retries so far: {retries.get(url, 0)} / 5\n")
                    delete_urls.append(url)
                    retries[url] = retries.get(url, 0) + 1

    progress.close()


def construct_delete_urls_from_ids(ids: list, type: str) -> set[str]:
    delete_urls = set()
    for record_id in ids:
        if record_id in VALIDATION_TYPE_TEXTS:
            continue
        if TYPE_PREFIX in record_id:
            delete_urls.add(CTX.get_base_url() + type + "/" + record_id)
    return delete_urls


def build_node_map():
    validation_types = utils.get_ids_for_record_type_matching_prefix("validationType")
    if not validation_types:
        utils.log("No validationTypes found to delete...")
    else:
        root_urls = utils.get_root_urls_for_validation_types(validation_types)
        for root_url in root_urls:
            utils.build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)
    print()


def delete_records():
    if not GLOBAL_NODE_MAP:
        utils.log("There is nothing to delete...")
    else:
        process_node_map_and_delete_records(GLOBAL_NODE_MAP)


def process_node_map_and_delete_records(global_node_map):
    global TOTAL_RECORD_DELETIONS, TOTAL_PROCESSED_RECORDS, TOTAL_PREFIX_MATCHES
    """
    A node is deleted only when no other node references it
    """

    remaining_parent_count = {
        url: len(node.parents)
        for url, node in global_node_map.items()
    }

    deletion_queue = deque()
    for url, count in remaining_parent_count.items():
        if count == 0:
            deletion_queue.append(url)

    processed: set[str] = set()
    TOTAL_PREFIX_MATCHES = get_total_matching_prefixed_records()
    progress = tqdm(total=TOTAL_PREFIX_MATCHES, desc="Deleting and/or updating records",
                    bar_format="{l_bar}{bar:30}{r_bar}")
    while deletion_queue:
        url = deletion_queue.popleft()
        node = global_node_map[url]

        process_record(progress, node)
        TOTAL_PROCESSED_RECORDS += 1
        processed.add(url)

        for child in node.children:
            child_url = child.url
            if child_url in remaining_parent_count:
                remaining_parent_count[child_url] -= 1

                if remaining_parent_count[child_url] == 0:
                    deletion_queue.append(child_url)

    progress.close()
    print()
    check_for_unprocessed_nodes(global_node_map, processed)


def get_total_matching_prefixed_records() -> int:
    return sum(1 for node in GLOBAL_NODE_MAP.values() if node.record_id.startswith(TYPE_PREFIX))


def process_record(progress, node):
    global TOTAL_RECORD_DELETIONS, TOTAL_RECORD_UPDATES
    if node.record_type == "validationType":
        collect_text_ids(node)
        utils.break_dependency_to_top_groups(node.xml_content)
        utils.remove_action_links(node.xml_content)
        if update_record(node):
            CTX.log(
                f"ValidationType '{node.record_id}' was updated to original metadata new/update groups and not deleted")
            TOTAL_RECORD_UPDATES += 1
            progress.update(1)

    else:
        if prepare_url_and_possibly_delete(node):
            TOTAL_RECORD_DELETIONS += 1
            progress.update(1)


def collect_text_ids(node):
    text_id = node.xml_content.find(".//textId/linkedRecordId")
    if text_id is not None and text_id.text:
        VALIDATION_TYPE_TEXTS.add(text_id.text.strip())
    def_text_id = node.xml_content.find(".//defTextId/linkedRecordId")
    if def_text_id is not None and def_text_id.text:
        VALIDATION_TYPE_TEXTS.add(def_text_id.text.strip())


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        utils.log("Some records were not processed (and probably not deleted), check log for more info...")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def update_record(node):
    if DRY_RUN:
        CTX.log(f"  Dry run mode - not saving {node.new_record_id}\n")
        return True

    return utils.try_to_update_record(node, TOTAL_ERRORS)


def prepare_url_and_possibly_delete(node):
    if not f"{node.record_id}".startswith(TYPE_PREFIX):
        return False
    if DRY_RUN:
        return True

    return utils.prepare_and_delete_record(node, TOTAL_ERRORS)


def log_results():  # pragma: no cover
    if DRY_RUN:
        utils.log("[ Script ran in dry run mode ]")

    utils.log(f"  Total records updated: {TOTAL_RECORD_UPDATES}")
    utils.log(f"  Total records and presentations deleted: {TOTAL_RECORD_DELETIONS}")

    if TOTAL_PROCESSED_RECORDS != len(GLOBAL_NODE_MAP):
        utils.log(f"\n   Warning: The number of successfully processed records ({TOTAL_PROCESSED_RECORDS})"
                  f" are less than the expected total of {len(GLOBAL_NODE_MAP)}!")

    if TOTAL_ERRORS:
        print("\nWarning! There were errors reported during processing, please check the log file for details.")
        CTX.log("=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            CTX.log(f" > {error}")
    else:
        utils.log("  No errors reported.")


if __name__ == "__main__":  # pragma: no cover
    main()
