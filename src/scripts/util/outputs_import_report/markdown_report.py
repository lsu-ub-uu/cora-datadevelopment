import os
from html import escape

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from fedora_to_cora.persons_migrate import PersonMigrationSummary
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    RELATION_ERRORS_LABEL,
    STATUS_LABELS,
    PERSON_FAILURE_NOTICE,
    extract_export_date,
    format_publication_type_pid_groups,
    format_yes_no,
    generate_relation_error_data,
    generate_person_report_data,
    generate_report_data,
    generate_setup_for_report,
    generate_summary_tables,
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
    person_summary: PersonMigrationSummary | None = None,
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

    lines.append("## Summary\n")
    for migration, counts in generate_summary_tables(
        status_counts, relation_results or [], person_summary
    ).items():
        lines.append(f"### {migration}\n")
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status, count in counts.items():
            lines.append(f"| {status} | {count} |")
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

    if person_summary is not None:
        _append_person_migration_section(lines, person_summary)

    _append_relation_errors_section(lines, relation_results or [])

    with open(filepath, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines))
    print(f"Markdown report saved to {filepath}")


def _append_person_migration_section(lines: list[str], summary: PersonMigrationSummary):
    counts, errors = generate_person_report_data(summary)
    lines.extend(["## Person Migration\n", "| Metric | Count |", "|--------|-------|"])
    lines.extend(f"| {label} | {count} |" for label, count in counts.items())
    lines.append("")
    if summary.has_failures:
        lines.extend([PERSON_FAILURE_NOTICE, ""])
    if errors:
        lines.extend(
            [
                "| Error Message | Occurrences | Authority PIDs / XML files |",
                "|---------------|-------------|----------------------------|",
            ]
        )
        for error in errors:
            cells = [
                escape(value.replace("|", " ").replace("\n", " ")) for value in error
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")


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
