import os
from xml.etree import ElementTree as ET

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from fedora_to_cora.persons_migrate import PersonMigrationSummary
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    RELATION_ERRORS_LABEL,
    STATUS_LABELS,
    PERSON_FAILURE_NOTICE,
    extract_export_date,
    format_yes_no,
    generate_relation_error_data,
    generate_person_report_data,
    generate_report_data,
    generate_setup_for_report,
    generate_summary_tables,
    group_error_pids_by_publication_type,
    resolve_target_system,
)


def save_html_report(
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
    domain, timestamp, filepath = generate_setup_for_report(xml_dir, output_dir, "html")

    os.makedirs(output_dir, exist_ok=True)

    target_system = resolve_target_system(system, cora_url)
    dry_run = format_yes_no(not apply)
    with_binaries = format_yes_no(binaries)
    export_date = extract_export_date(xml_dir)

    html = ET.Element("html")
    head = ET.SubElement(html, "head")
    title = ET.SubElement(head, "title")
    title.text = f"Migration Report ({timestamp})"
    ET.SubElement(head, "meta", attrib={"charset": "utf-8"})
    style = ET.SubElement(head, "style")
    style.text = "body{font-family:sans-serif;}table{border-collapse:collapse;margin-bottom:2em;}th,td{border:1px solid #ccc;padding:6px;vertical-align:text-top;}th{background:#75598e;color:#fff;}"

    body = ET.SubElement(html, "body")
    h1 = ET.SubElement(body, "h1")
    h1.text = f"Migration Report ({timestamp})"
    p = ET.SubElement(body, "p")
    p.text = f"Total records processed: {sum(status_counts.values())}"

    p_source = ET.SubElement(body, "p")
    p_source.text = f"Export date: {export_date}"

    p_meta = ET.SubElement(body, "p")
    p_meta.text = (
        f"Domain: {domain} | Target system: {target_system} | "
        f"Dry run: {dry_run} | With binaries: {with_binaries}"
    )

    h2_counts = ET.SubElement(body, "h2")
    h2_counts.text = "Summary"
    for migration, counts in generate_summary_tables(
        status_counts, relation_results or [], person_summary
    ).items():
        ET.SubElement(body, "h3").text = migration
        table_counts = ET.SubElement(body, "table")
        tr_head = ET.SubElement(table_counts, "tr")
        for col in ["Status", "Count"]:
            ET.SubElement(tr_head, "th").text = col
        for status, count in counts.items():
            tr = ET.SubElement(table_counts, "tr")
            ET.SubElement(tr, "td").text = status
            ET.SubElement(tr, "td").text = str(count)

    for category in ERROR_CATEGORIES_IN_ORDER:
        error_dict = errors.get(category, {})
        if error_dict:
            h2 = ET.SubElement(body, "h2")
            h2.text = f"{STATUS_LABELS[category]}"
            table = ET.SubElement(body, "table")
            tr_head = ET.SubElement(table, "tr")
            for col in ["Error Message", "Occurrences", "PIDs by publication type"]:
                th = ET.SubElement(tr_head, "th")
                th.text = col
            for error_msg, pids in error_dict.items():
                tr = ET.SubElement(table, "tr")
                td1 = ET.SubElement(tr, "td")
                td1.text = error_msg.replace("|", " ").replace("\n", " ")
                td2 = ET.SubElement(tr, "td")
                td2.text = str(len(pids))
                td3 = ET.SubElement(tr, "td")
                publication_type_groups = grouped_error_pids.get(category, {}).get(
                    error_msg, {}
                )
                for publication_type, grouped_pids in sorted(
                    publication_type_groups.items()
                ):
                    group = ET.SubElement(td3, "div")
                    label = ET.SubElement(group, "strong")
                    label.text = f"{publication_type}: "
                    label.tail = ", ".join(grouped_pids)

    if person_summary is not None:
        _append_person_migration_section(body, person_summary)

    _append_relation_errors_section(body, relation_results or [])

    html_str = ET.tostring(html, encoding="unicode", method="html")
    doctype = "<!DOCTYPE html>\n"
    with open(filepath, "w", encoding="utf-8") as file_obj:
        file_obj.write(doctype + html_str)
    print(f"HTML report saved to {filepath}")


def _append_person_migration_section(body: ET.Element, summary: PersonMigrationSummary):
    ET.SubElement(body, "h2").text = "Person Migration"
    counts, errors = generate_person_report_data(summary)
    table = ET.SubElement(body, "table")
    header = ET.SubElement(table, "tr")
    for label in ("Metric", "Count"):
        ET.SubElement(header, "th").text = label
    for label, count in counts.items():
        row = ET.SubElement(table, "tr")
        ET.SubElement(row, "td").text = label
        ET.SubElement(row, "td").text = str(count)
    if summary.has_failures:
        ET.SubElement(body, "p").text = PERSON_FAILURE_NOTICE
    if errors:
        table = ET.SubElement(body, "table")
        header = ET.SubElement(table, "tr")
        for label in ("Error Message", "Occurrences", "Authority PIDs / XML files"):
            ET.SubElement(header, "th").text = label
        for error in errors:
            row = ET.SubElement(table, "tr")
            for value in error:
                ET.SubElement(row, "td").text = value.replace("|", " ").replace(
                    "\n", " "
                )


def _append_relation_errors_section(
    body: ET.Element, relation_results: list[OutputRelationMigrationResult]
):
    relation_errors = generate_relation_error_data(relation_results)
    if not relation_errors:
        return

    h2 = ET.SubElement(body, "h2")
    h2.text = RELATION_ERRORS_LABEL
    table = ET.SubElement(body, "table")
    tr_head = ET.SubElement(table, "tr")
    for col in ["Error Message", "Occurrences", "PIDs"]:
        th = ET.SubElement(tr_head, "th")
        th.text = col
    for error_msg, pids in relation_errors.items():
        tr = ET.SubElement(table, "tr")
        td1 = ET.SubElement(tr, "td")
        td1.text = error_msg.replace("|", " ").replace("\n", " ")
        td2 = ET.SubElement(tr, "td")
        td2.text = str(len(pids))
        td3 = ET.SubElement(tr, "td")
        td3.text = ", ".join(pids)
