from copy import deepcopy
from common.arg_parser import create_argument_parser, cora_url_argument
from common.logging_config import configure_logging
from common.threads import run_with_threads
from cora.delete_record import delete_record
from cora.create import create_record, is_success_result
from cora.get_incoming_links import get_incoming_links
from cora.context import CoraContext, Context
from cora.get_record import get_record
from cora.update import update_record

unique_constraint_paths = [
    "./data/*/recordInfo/oldId",
    "./data/organisation/identifier[@type='organisationNumber']",
]


def main():
    """
    This script is a one-off utility to fix records of a specified type that have an oldId of "0" by
    creating a new record with the same data but without the oldId, updating all incoming links from diva-output records to point to the new record,
    and then deleting the original record. It also handles removing and restoring unique constraint values to avoid conflicts during the process.
    """

    print("Updating record links...")
    args = _parse_args()
    configure_logging()
    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )

    original_record = get_record(context, args.record_type, args.old_record_id)
    record_copy = _copy_as_new_without_record_info_id(original_record)

    removed_unique_constraints = _remove_and_remember_unique_constraints(
        record_copy, unique_constraint_paths
    )
    old_id = original_record.findtext("./data/*/recordInfo/oldId")

    print(f"Fetched original record with old ID {old_id}")
    assert old_id is not None, "Old ID not found in original record"

    print("Creating copy of original record with new ID...")
    new_record_data = record_copy.find("./data/*")
    assert new_record_data is not None, "New record data not found"
    create_result = create_record(
        new_record_data, record_type=args.record_type, context=context
    )

    if not is_success_result(create_result):
        print("Failed to create new record:", create_result.error)
        return

    print("New record created with ID:", create_result.record_id)
    new_record_id = create_result.record_id

    print("Fetching incoming links to the original record...")
    incoming_links = get_incoming_links(context, args.record_type, args.old_record_id)
    assert all(
        link.findtext("./from/linkedRecordType") == "diva-output"
        for link in incoming_links
    ), "Not all incoming links are diva-output"

    print("Found", len(incoming_links), "incoming links from diva-output records")

    output_record_ids = [
        link.findtext("./from/linkedRecordId") for link in incoming_links
    ]

    results = run_with_threads(
        output_record_ids,
        lambda record_id: _update_diva_output(
            context, record_id, args.old_record_id, new_record_id, args.record_link_path
        ),
        context.get_workers(),
        "Updating diva-output records",
    )

    print(
        f"Finished updating links. {sum(result.success for result in results)} out of {len(results)} records updated successfully."
    )

    for result in results:
        if not result.success:
            print("Failed to update diva-output record:", result.error)

    print("Deleting original record...")
    delete_record(
        record_type=args.record_type, record_id=args.old_record_id, context=context
    )

    print("Restoring unique constraint values to new record...")
    new_record = get_record(context, args.record_type, new_record_id)
    _restore_removed_unique_constraints(new_record, removed_unique_constraints)
    update_result = update_record(new_record, context)
    if update_result.success:
        print("Successfully updated new record with removed unique constraint values")
    else:
        print(
            "Failed to update new record with removed unique constraint values:",
            update_result.error,
        )

    print("Record link update process completed.")


def _update_diva_output(
    context: Context,
    output_id: str,
    old_record_id: str,
    new_record_id: str,
    record_link_path: str,
):
    record = get_record(context, "diva-output", output_id)
    for link in record.findall(record_link_path):
        if link.text == old_record_id:
            link.text = new_record_id

    return update_record(record, context)


def _copy_as_new_without_record_info_id(record):
    record_copy = deepcopy(record)

    copied_record_info = record_copy.find("./data/*/recordInfo")
    assert copied_record_info is not None, "Copied record info not found"

    for tag in ("id", "type", "createdBy", "tsCreated", "updated"):
        element = copied_record_info.find(f"./{tag}")
        if element is not None:
            copied_record_info.remove(element)

    return record_copy


def _remove_and_remember_unique_constraints(record, paths):
    removed_elements_by_path = {}

    for path in paths:
        parent_path, tag = path.rsplit("/", 1)
        removed_elements = []

        for parent_index, parent in enumerate(record.findall(parent_path)):
            for element in list(parent.findall(tag)):
                removed_elements.append((parent_index, deepcopy(element)))
                parent.remove(element)

        removed_elements_by_path[path] = removed_elements

    return removed_elements_by_path


def _restore_removed_unique_constraints(record, removed_elements_by_path):
    for path, removed_elements in removed_elements_by_path.items():
        if not removed_elements:
            continue

        parent_path, _ = path.rsplit("/", 1)
        parents = record.findall(parent_path)
        assert parents, f"Parent path not found for restoring removed elements: {path}"

        for parent_index, element in removed_elements:
            assert parent_index < len(
                parents
            ), f"Parent index out of range while restoring path: {path}"
            parents[parent_index].append(deepcopy(element))


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            **cora_url_argument,
            "--system": {
                "default": "pre",
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": "migration@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--record-type": {
                "help": "The type of record to update links for",
            },
            "--old-record-id": {
                "help": "The ID of the record to update links for",
            },
            "--record-link-path": {
                "default": "./data/output/subject/topic/linkedRecordId",
                "help": "The XML path to the record link elements in diva-output records",
            },
        },
    )
    # ./data/output/name/affiliation/organisation/linkedRecordId
    return parser.parse_args()


if __name__ == "__main__":
    main()
