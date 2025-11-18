import xml.etree.ElementTree as ET
from typing import Callable
from common.threads import run_with_threads
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from cora.context import Context
from db_to_cora.update_relations import update_relations


def records_import(
    context: Context,
    record_type: str,
    source_records: list[ET.Element],
    transform_function: Callable[[ET.Element], ET.Element],
    relations_mapping: list[tuple[str, str]] | None = None,
    apply: bool = False,
):
    context.log(
        f"Importing records for type: {record_type} to Cora system: {context.get_system()}"
    )
    print(
        f"Importing records for type: {record_type} to Cora system: {context.get_system()}"
    )
    print(f"Output logged to {context.get_log_file_path()}")

    if apply:
        apply_import(
            record_type, source_records, transform_function, context, relations_mapping
        )
    else:
        dry_run(
            record_type,
            source_records,
            transform_function,
            context,
        )


def apply_import(
    record_type: str,
    source_records: list[ET.Element],
    transform_function: Callable[[ET.Element], ET.Element],
    context: Context,
    relations_mapping: list[tuple[str, str]] | None,
):
    def process_record(source_record: ET.Element):
        transformed_record = transform_function(source_record)
        result = create_record(
            transformed_record, record_type=record_type, context=context
        )
        if is_success_result(result):
            return source_record, result.response_data
        else:
            context.log(f"Failed to create record: {result.error}", level="error")
            raise Exception(f"Record creation failed: {result.error}")

    record_mapping = run_with_threads(
        source_records,
        process_record,
        workers=context.get_workers(),
        desc=f"Creating {record_type} records",
    )
    print(f"Created {len(record_mapping)} records.")
    if relations_mapping:
        print(f"Updating relations for {len(record_mapping)} records.")
        update_relations(
            record_mapping,
            relations_mapping,
            record_type=record_type,
            link_name=record_type.split("-")[-1],
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
