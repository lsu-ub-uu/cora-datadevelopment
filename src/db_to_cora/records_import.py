import xml.etree.ElementTree as ET
from typing import Callable

from tqdm import tqdm
from common.threads import run_with_threads
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from cora.context import Context, CoraContext
from db_to_cora.update_relations import RelationMapping, update_relations
from multiprocessing import Pool

from db_to_cora.publisher_transform import transform_publisher
from db_to_cora.funder_transform import transform_funder
from db_to_cora.journal_transform import transform_journal
from db_to_cora.subject_programme_course_transform import (
    transform_subject,
    transform_course,
    transform_programme,
)
from db_to_cora.series_transform import transform_series

context = None


def records_import(
    system: str,
    login_id: str,
    app_token: str,
    record_type: str,
    source_records: list[ET.Element],
    transform_function: Callable[[ET.Element], ET.Element],
    relation_mappings: list[RelationMapping] | None = None,
    apply: bool = False,
):
    # context.log(
    #     f"Importing records for type: {record_type} to Cora system: {context.get_system()}"
    # )
    print(f"Importing records for type: {record_type} to Cora system: {system}")
    # print(f"Output logged to {context.get_log_file_path()}")

    if apply:
        apply_import(
            system, login_id, app_token, record_type, source_records, relation_mappings
        )
    else:
        dry_run(
            system, login_id, app_token, record_type, source_records, transform_function
        )


def _init_context(system: str, login_id: str, app_token: str):
    global context
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)


def _migrate_record(
    source_record: ET.Element,
):
    assert context is not None, "Context must be initialized before migrating records"

    transform_function = transform_journal
    # match record_type:
    #     case "diva-publisher":
    #         transform_function = transform_publisher
    #     case "diva-funder":
    #         transform_function = transform_funder
    #     case "diva-journal":
    #         transform_function = transform_journal
    #     case "diva-series":
    #         transform_function = transform_series
    #     case "diva-subject":
    #         transform_function = transform_subject
    #     case "diva-course":
    #         transform_function = transform_course
    #     case "diva-programme":
    #         transform_function = transform_programme

    # assert (
    #     transform_function is not None
    # ), f"No transform function defined for record type {record_type}"

    transformed_record = transform_function(source_record)
    result = create_record(
        transformed_record, record_type="diva-journal", context=context
    )
    if is_success_result(result):
        return source_record, result.response_data
    else:
        old_id = source_record.findtext("./old_id")
        if result.error and (
            f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
            in result.error
        ):
            context.log(
                f"Record with old id {old_id} already exists. Skipping creation.",
                level="warning",
            )
            return source_record, None
        context.log(f"Failed to create record: {result.error}", level="error")
        raise Exception(f"Record creation failed: {result.error}")


def apply_import(
    system: str,
    login_id: str,
    app_token: str,
    record_type: str,
    source_records: list[ET.Element],
    relation_mappings: list[RelationMapping] | None = None,
):
    record_mapping = []

    with (
        Pool(
            processes=16,
            initializer=_init_context,
            initargs=(
                system,
                login_id,
                app_token,
            ),
        ) as pool,
        tqdm(total=len(source_records), desc="Importing records") as progress,
    ):
        for result in pool.imap_unordered(_migrate_record, source_records):
            # counts[result.status] += 1
            record_mapping.append(result)
            # progress.set_postfix_str(
            #     f"✅ {counts['SUCCESS']} | ⚠️ {counts['CLASSIC_QUALITY']} | ❌ {counts['FAILED']} | ➡️ {counts['SKIPPED']} | ⛔{counts['INPUT_VALIDATION_FAILED']}"
            # )
            progress.update(1)

    print(f"Created {len(record_mapping)} records.")
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)
    if relation_mappings:
        print(f"Updating relations for {len(record_mapping)} records.")
        update_relations(
            record_mapping,
            relation_mappings,
            record_type=record_type,
            context=context,
        )


def dry_run(
    record_type: str,
    source_records: list[ET.Element],
    transform_function: Callable[[ET.Element], ET.Element],
    context: Context,
):
    transformed_records = [transform_function(record) for record in source_records]
    validation_results = run_with_threads(
        transformed_records,
        lambda record: validate_record(
            record, record_type=record_type, context=context
        ),
        workers=context.get_workers(),
        desc=f"Validating {record_type} records",
    )
    valid_count = sum(1 for valid, _ in validation_results if valid)
    invalid_count = sum(1 for valid, _ in validation_results if not valid)
    print(f"✅ {valid_count} valid")
    if invalid_count > 0:
        print(f"❌ {invalid_count} invalid")
