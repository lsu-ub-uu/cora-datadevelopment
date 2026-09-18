from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.console_report import print_console_report
from scripts.util.outputs_import_report.html_report import save_html_report
from scripts.util.outputs_import_report.markdown_report import save_markdown_report


def save_reports(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
    relation_results: list[OutputRelationMigrationResult] | None = None,
):
    relation_results = relation_results or []
    save_html_report(
        results,
        xml_dir=xml_dir,
        system=system,
        output_dir=output_dir,
        relation_results=relation_results,
    )
    save_markdown_report(
        results,
        xml_dir=xml_dir,
        system=system,
        output_dir=output_dir,
        relation_results=relation_results,
    )
    print_console_report(results, relation_results=relation_results)
