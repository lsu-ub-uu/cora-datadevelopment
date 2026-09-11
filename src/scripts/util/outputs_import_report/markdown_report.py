import os

from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    STATUS_LABELS,
    format_publication_type_pid_groups,
    generate_report_data,
    generate_setup_for_report,
    group_error_pids_by_publication_type,
)


def save_markdown_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    status_counts, errors = generate_report_data(results)
    grouped_error_pids = group_error_pids_by_publication_type(results)
    domain, timestamp, filepath = generate_setup_for_report(xml_dir, output_dir, "md")

    os.makedirs(output_dir, exist_ok=True)

    lines = []
    lines.append(f"# Migration Report ({timestamp})\n")
    lines.append(f"**Total records processed:** {sum(status_counts.values())}")
    lines.append("")
    lines.append(f"**Source XML Directory:** `{xml_dir}`  ")
    lines.append(f"**Domain: {domain} | Target System:** `{system}`  ")
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

    with open(filepath, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines))
    print(f"Markdown report saved to {filepath}")
