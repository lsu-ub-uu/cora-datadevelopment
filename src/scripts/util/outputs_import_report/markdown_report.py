import os

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    RELATION_ERRORS_LABEL,
    STATUS_LABELS,
    extract_export_date,
    format_publication_type_pid_groups,
    format_yes_no,
    generate_relation_error_data,
    generate_report_data,
    generate_setup_for_report,
    group_error_pids_by_publication_type,
    resolve_target_system,
)


def save_markdown_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    apply: bool,
    binaries: bool,
    cora_url: str | None,
    output_dir: str = ".",
    relation_results: list[OutputRelationMigrationResult] | None = None,
):
    status_counts, errors = generate_report_data(results)
    grouped_error_pids = group_error_pids_by_publication_type(results)
    domain, timestamp, filepath = generate_setup_for_report(xml_dir, output_dir, "md")

    os.makedirs(output_dir, exist_ok=True)

    target_system = resolve_target_system(system, cora_url)
    dry_run = format_yes_no(not apply)
    with_binaries = format_yes_no(binaries)
    export_date = extract_export_date(xml_dir)

    lines = []
    lines.append(f"# Migration Report ({timestamp})\n")
    lines.append(f"**Total records processed:** {sum(status_counts.values())}")
    lines.append("")
    lines.append(f"**Export date:** `{export_date}`  ")
    lines.append(f"**Domain:** {domain}  ")
    lines.append(f"**Target system:** `{target_system}`  ")
    lines.append(f"**Dry run:** {dry_run}  ")
    lines.append(f"**With binaries:** {with_binaries}  ")
    lines.append("")

    lines.append("## Status Counts\n")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for status, count in status_counts.items():
        lines.append(f"| {STATUS_LABELS[status]} | {count} |")
    lines.append("")

    for category in ERROR_CATEGORIES_IN_ORDER:
        error_dict = errors.get(category, {})
        if error_dict:
            lines.append(f"## {STATUS_LABELS[category]}\n")
            lines.append("| Error Message | Occurrences | PIDs by publication type |")
            lines.append("|--------------|-------------|------|")
            for error_msg, pids in error_dict.items():
                publication_type_groups = grouped_error_pids.get(category, {}).get(
                    error_msg, {}
                )
                pid_str = format_publication_type_pid_groups(
                    publication_type_groups, "<br>"
                )
                lines.append(
                    f"| {error_msg.replace('|', ' ').replace(chr(10), ' ')} | {len(pids)} | {pid_str} |"
                )
            lines.append("")

    _append_relation_errors_section(lines, relation_results or [])

    with open(filepath, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines))
    print(f"Markdown report saved to {filepath}")


def _append_relation_errors_section(
    lines: list[str], relation_results: list[OutputRelationMigrationResult]
):
    relation_errors = generate_relation_error_data(relation_results)
    if not relation_errors:
        return

    lines.append(f"## {RELATION_ERRORS_LABEL}\n")
    lines.append("| Error Message | Occurrences | PIDs |")
    lines.append("|--------------|-------------|------|")
    for error_msg, pids in relation_errors.items():
        sanitized = error_msg.replace("|", " ").replace(chr(10), " ")
        lines.append(f"| {sanitized} | {len(pids)} | {', '.join(pids)} |")
    lines.append("")
