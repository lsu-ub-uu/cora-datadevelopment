from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts.util.outputs_import_report.console_report import print_console_report
from scripts.util.outputs_import_report.html_report import save_html_report
from scripts.util.outputs_import_report.markdown_report import save_markdown_report


def save_reports(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    save_html_report(results, xml_dir=xml_dir, system=system, output_dir=output_dir)
    save_markdown_report(results, xml_dir=xml_dir, system=system, output_dir=output_dir)
    print_console_report(results)
