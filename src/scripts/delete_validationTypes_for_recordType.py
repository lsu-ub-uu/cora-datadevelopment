from collections import deque

import validation_type_utils.common_utils as utils
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
TOTAL_PREFIX_MATCHES = 0
TOTAL_PROCESSED_RECORDS = 0
TOTAL_RECORD_DELETIONS = 0
TOTAL_RECORD_UPDATES = 0
TOTAL_PRESENTATION_DELETIONS = 0
TOTAL_ERRORS = []


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

    if DRY_RUN:
        utils.log(
            ">>> [SCRIPT IN DRY RUN MODE] - No changes will be applied to the system, use --apply to apply changes")

    delete_records_with_prefix()


def delete_records_with_prefix():
    utils.log("Deleting all records and presentations that use prefix: " + TYPE_PREFIX)

    utils.log("=== Deleting all presentations ===")
    delete_presentations()
    print()

    utils.log("=== Building node map ===")
    validation_types = utils.get_ids_for_record_type_matching_prefix("validationType")
    if not validation_types:
        utils.log("No validationTypes found to delete...")
    else:
        print("\n...artistic pause...")
        root_urls = utils.get_root_urls_for_validation_types(validation_types)
        for root_url in root_urls:
            utils.build_node_map_from_child_references(root_url, GLOBAL_NODE_MAP)

    print()
    utils.log("=== Deleting records ===")

    if not GLOBAL_NODE_MAP:
        utils.log("There is nothing to delete...")
    else:
        print("\n~ Heavy metal riff playing ~")
        process_node_map_and_delete_records(GLOBAL_NODE_MAP)

    utils.log("=== Script finished ===")
    log_results()

    print(f"\n=== Processing completed. Output logged to {CTX.get_log_file_path()} ===")


def delete_presentations():
    presentation_ids = utils.get_ids_for_record_type_matching_prefix("presentation")
    delete_urls = deque(construct_delete_urls_from_ids(presentation_ids))

    if not delete_urls:
        utils.log("No presentations found to delete...")
        return

    print("\n~ Heavy metal riff playing ~")
    try_to_delete_presentations(delete_urls)


def try_to_delete_presentations(delete_urls: deque[str]):
    global TOTAL_PRESENTATION_DELETIONS
    total = len(delete_urls)
    retries: dict[str, int] = {}
    while delete_urls:
        url = delete_urls.popleft()
        if DRY_RUN:
            TOTAL_PRESENTATION_DELETIONS += 1
            print(f"Presentations annihilated from existance: {TOTAL_PRESENTATION_DELETIONS} / {total}", end="\r",
                  flush=True)
        else:
            deleted = utils.try_to_delete_record(url, TOTAL_ERRORS)
            if deleted:
                TOTAL_PRESENTATION_DELETIONS += 1
                print(f"Presentations annihilated from existance: {TOTAL_PRESENTATION_DELETIONS} / {total}", end="\r",
                      flush=True)
            else:
                if retries.get(url, 0) >= 5:
                    TOTAL_ERRORS.append("Failed to delete " + url + " after 5 retries!")
                else:
                    CTX.log(
                        f"   - Failed to delete record. Will retry... number of retries so far: {retries.get(url, 0)} / 5\n")
                    delete_urls.append(url)
                    retries[url] = retries.get(url, 0) + 1


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

    while deletion_queue:
        url = deletion_queue.popleft()
        node = global_node_map[url]

        TOTAL_PROCESSED_RECORDS += 1
        if TYPE_PREFIX in node.record_id:
            TOTAL_PREFIX_MATCHES += 1
        process_record(global_node_map, node)

        processed.add(url)

        for child in node.children:
            child_url = child.url
            if child_url in remaining_parent_count:
                remaining_parent_count[child_url] -= 1

                if remaining_parent_count[child_url] == 0:
                    deletion_queue.append(child_url)

    print()
    check_for_unprocessed_nodes(global_node_map, processed)


def process_record(global_node_map, node):
    global TOTAL_RECORD_DELETIONS, TOTAL_RECORD_UPDATES
    if node.record_type == "validationType":
        CTX.log(f"ValidationType '{node.record_id}' was updated to original metadata new/update groups and not deleted")
        utils.break_dependency_to_top_groups(node.xml_content)
        utils.remove_action_links(node.xml_content)
        if update_record(node):
            TOTAL_RECORD_UPDATES += 1

    else:
        if prepare_url_and_possibly_delete(node):
            TOTAL_RECORD_DELETIONS += 1
            print(f"Records purged from this world: {TOTAL_RECORD_DELETIONS} / {len(global_node_map)}", end="\r",
                  flush=True)


def log_results():  # pragma: no cover
    if DRY_RUN:
        utils.log("[ Script ran in dry run mode ]")
    total_changed_or_updated = TOTAL_RECORD_UPDATES + TOTAL_RECORD_DELETIONS

    utils.log(f"  Total presentations deleted: {TOTAL_PRESENTATION_DELETIONS}")
    utils.log(f"  Total records updated: {TOTAL_RECORD_UPDATES}")
    utils.log(f"  Total records deleted: {TOTAL_RECORD_DELETIONS}")
    utils.log(
        f"  Total updated or deleted records out of matching prefixes: {total_changed_or_updated} / {TOTAL_PREFIX_MATCHES}")

    if TOTAL_PROCESSED_RECORDS == len(GLOBAL_NODE_MAP):
        utils.log("  > All records in node map were processed...")
    else:
        utils.log(
            f"\n   Warning: The number of successfully processed records ({TOTAL_PROCESSED_RECORDS}) are less than the expected total of {len(GLOBAL_NODE_MAP)}!")

    if TOTAL_ERRORS:
        print("\nWarning! There were errors reported during processing, please check the log file for details.")
        CTX.log("=== Errors reported ===")
        for (error) in TOTAL_ERRORS:
            CTX.log(f" > {error}")
    else:
        utils.log("  No errors reported.")


def check_for_unprocessed_nodes(global_node_map, processed: set[str]):
    unprocessed = [url for url in global_node_map if url not in processed]
    if unprocessed:
        utils.log("Some records were not processed (and probably not deleted), check log for more info...")
        for url in unprocessed:
            TOTAL_ERRORS.append("Warning: Record: " + url + " was never processed")


def prepare_url_and_possibly_delete(node):
    if not f"{node.record_id}".startswith(TYPE_PREFIX):
        return False
    if DRY_RUN:
        return True

    return utils.prepare_and_delete_record(node, TOTAL_ERRORS)


# XML utilities ----------------------------------
def construct_delete_urls_from_ids(ids: list) -> set[str]:
    delete_urls = set()
    for record_id in ids:
        if TYPE_PREFIX in record_id:
            delete_urls.add(CTX.get_base_url() + "presentation/" + record_id)
    return delete_urls


def update_record(node):
    if DRY_RUN:
        CTX.log(f"  Dry run mode - not saving {node.new_record_id}\n")
        return True

    return utils.try_to_update_record(node, TOTAL_ERRORS)


if __name__ == "__main__":  # pragma: no cover
    main()
