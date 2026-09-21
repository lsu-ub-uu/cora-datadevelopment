from rich.console import Console
from rich.table import Table

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.report_data import (
    extract_export_date,
    format_yes_no,
    generate_report_data,
    resolve_target_system,
)


def print_console_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    apply: bool,
    binaries: bool,
    cora_url: str | None,
    relation_results: list[OutputRelationMigrationResult] | None = None,
):
    """Prints the output of generate_report_data using a table from the rich library."""
    console = Console()
    status_counts, _ = generate_report_data(results)

    target_system = resolve_target_system(system, cora_url)
    console.print(f"Export date: {extract_export_date(xml_dir)}")
    console.print(f"Target system: {target_system}")
    console.print(f"Dry run: {format_yes_no(not apply)}")
    console.print(f"With binaries: {format_yes_no(binaries)}")

    table = Table(title="Migration Status Counts")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    for status, count in status_counts.items():
        table.add_row(status, str(count))
    console.print(table)
