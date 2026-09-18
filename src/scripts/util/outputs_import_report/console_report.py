from rich.console import Console
from rich.table import Table

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    RELATION_ERRORS_LABEL,
    format_publication_type_pid_groups,
    generate_relation_error_data,
    generate_report_data,
    group_error_pids_by_publication_type,
)


def print_console_report(
    results: list[OutputMigrationResult],
    relation_results: list[OutputRelationMigrationResult] | None = None,
):
    """Prints the output of generate_report_data using a table from the rich library."""
    console = Console()
    status_counts, errors = generate_report_data(results)
    grouped_error_pids = group_error_pids_by_publication_type(results)

    table = Table(title="Migration Status Counts")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    for status, count in status_counts.items():
        table.add_row(status, str(count))
    console.print(table)

    for category in ERROR_CATEGORIES_IN_ORDER:
        if errors.get(category):
            error_dict = errors[category]
            if error_dict:
                error_table = Table(title=f"{category} Errors", show_lines=True)
                error_table.add_column("Error Message", style="red")
                error_table.add_column("Occurrences", justify="right")
                error_table.add_column("PIDs by publication type", style="cyan")
                for error_msg, pids in error_dict.items():
                    publication_type_groups = grouped_error_pids.get(category, {}).get(
                        error_msg, {}
                    )
                    pid_groups = format_publication_type_pid_groups(
                        publication_type_groups
                    )
                    error_table.add_row(error_msg, str(len(pids)), pid_groups)
                console.print(error_table)

    _print_relation_errors(console, relation_results or [])


def _print_relation_errors(
    console: Console, relation_results: list[OutputRelationMigrationResult]
):
    relation_errors = generate_relation_error_data(relation_results)
    if not relation_errors:
        return

    table = Table(title=RELATION_ERRORS_LABEL, show_lines=True)
    table.add_column("Error Message", style="red")
    table.add_column("Occurrences", justify="right")
    table.add_column("PIDs", style="cyan")
    for error_msg, pids in relation_errors.items():
        table.add_row(error_msg, str(len(pids)), ", ".join(pids))
    console.print(table)
