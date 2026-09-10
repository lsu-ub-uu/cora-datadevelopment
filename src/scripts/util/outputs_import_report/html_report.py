import os
from xml.etree import ElementTree as ET

from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts.util.outputs_import_report.report_data import (
    ERROR_CATEGORIES_IN_ORDER,
    STATUS_LABELS,
    generate_report_data,
    generate_setup_for_report,
    group_error_pids_by_publication_type,
)


def save_html_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    status_counts, errors = generate_report_data(results)
    grouped_error_pids = group_error_pids_by_publication_type(results)
    domain, timestamp, filepath = generate_setup_for_report(xml_dir, output_dir, "html")

    os.makedirs(output_dir, exist_ok=True)

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

    p2 = ET.SubElement(body, "p")
    p2.text = f"Domain: {domain} | Target System: {system}"

    h2_counts = ET.SubElement(body, "h2")
    h2_counts.text = "Status Counts"
    table_counts = ET.SubElement(body, "table")
    tr_head = ET.SubElement(table_counts, "tr")
    for col in ["Status", "Count"]:
        th = ET.SubElement(tr_head, "th")
        th.text = col
    for status, count in status_counts.items():
        tr = ET.SubElement(table_counts, "tr")
        td1 = ET.SubElement(tr, "td")
        td1.text = STATUS_LABELS[status]
        td2 = ET.SubElement(tr, "td")
        td2.text = str(count)

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

    html_str = ET.tostring(html, encoding="unicode", method="html")
    doctype = "<!DOCTYPE html>\n"
    with open(filepath, "w", encoding="utf-8") as file_obj:
        file_obj.write(doctype + html_str)
    print(f"HTML report saved to {filepath}")
