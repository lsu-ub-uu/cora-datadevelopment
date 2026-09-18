import datetime
import os
import re

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult

STATUS_LABELS = {
    "SUCCESS": "✅ Successfully imported as data quality DiVA 2026",
    "CLASSIC_QUALITY": "⚠️ Validation errors (imported as classic data quality)",
    "FAILED": "❌ Failed to import",
    "SKIPPED": "➡️ Skipped",
    "INPUT_VALIDATION_FAILED": "⛔ Source XML validation failed",
}

ERROR_CATEGORIES_IN_ORDER = [
    "INPUT_VALIDATION_FAILED",
    "FAILED",
    "CLASSIC_QUALITY",
    "SKIPPED",
]

RELATION_ERRORS_LABEL = "❌ Failed to migrate relations"


def generate_relation_error_data(
    relation_results: list[OutputRelationMigrationResult],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for result in relation_results:
        if result.status != "FAILED" or result.error is None:
            continue
        errors.setdefault(result.error, []).append(result.pid)

    for error in errors:
        errors[error] = sorted(errors[error])

    sorted_items = sorted(errors.items(), key=lambda item: len(item[1]), reverse=True)
    return dict(sorted_items)


def generate_report_data(results: list[OutputMigrationResult]):
    print("==== Migration Report ====")
    print(f"Total records processed: {len(results)}")
    status_counts = {
        "SUCCESS": 0,
        "CLASSIC_QUALITY": 0,
        "FAILED": 0,
        "SKIPPED": 0,
        "INPUT_VALIDATION_FAILED": 0,
    }
    error_categories = {
        "FAILED": {},
        "CLASSIC_QUALITY": {},
        "SKIPPED": {},
        "INPUT_VALIDATION_FAILED": {},
    }

    for result in results:
        status_counts[result.status] += 1
        if result.errors is not None:
            for error in result.errors:
                if error not in error_categories[result.status]:
                    error_categories[result.status][error] = []

                error_categories[result.status][error].append(result.pid)

    for category in error_categories:
        for error in error_categories[category]:
            error_categories[category][error] = sorted(
                error_categories[category][error]
            )

        sorted_items = sorted(
            error_categories[category].items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )
        error_categories[category] = dict(sorted_items)

    return (status_counts, error_categories)


def group_error_pids_by_publication_type(results: list[OutputMigrationResult]):
    grouped_pids = {}
    for result in results:
        if result.errors is None:
            continue

        publication_type = result.publication_type or "UNKNOWN"
        for error in result.errors:
            grouped_pids.setdefault(result.status, {}).setdefault(error, {}).setdefault(
                publication_type, []
            ).append(result.pid)

    for error_group in grouped_pids.values():
        for publication_type_group in error_group.values():
            for publication_type, pids in publication_type_group.items():
                publication_type_group[publication_type] = sorted(pids)

    return grouped_pids


def format_publication_type_pid_groups(
    publication_type_groups: dict[str, list[str]], group_separator: str = "\n"
):
    return group_separator.join(
        f"{publication_type}: {', '.join(pids)}"
        for publication_type, pids in sorted(publication_type_groups.items())
    )


def generate_setup_for_report(
    xml_dir: str, output_dir: str = ".", filetype: str = "md"
):
    domain_match = re.search(r"fedora_xml/(.+)/.+", xml_dir)
    domain = domain_match.group(1) if domain_match else "unknown"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    filename = f"outputs-import-{domain}-{timestamp}.{filetype}"
    filepath = os.path.join(output_dir, filename)
    return (domain, timestamp, filepath)
