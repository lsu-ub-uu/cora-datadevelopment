from rich.console import Console
from rich.table import Table
import os
import sys
import time
from xml.etree import ElementTree as ET
from common.arg_parser import (
    create_argument_parser,
    classic_arguments,
    cora_url_argument,
)
from common.logging_config import configure_logging
from cora.context import CoraContext
from fedora_to_cora.output_migrate import output_migrate, OutputMigrationResult
from common.xml_validate import validate_xml, XMLValidationError
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec
from common.common_data import read_source_xml
from common.print_logo import print_logo
from multiprocessing import Pool
from tqdm import tqdm
import datetime
import re

context = None
with_binaries = False
apply = False
fedora_url = ""

status_labels = {
    "SUCCESS": "✅ Successfully imported as data quality DiVA 2026",
    "CLASSIC_QUALITY": "⚠️ Validation errors (imported as classic data quality)",
    "FAILED": "❌ Failed to import",
    "SKIPPED": "➡️ Skipped",
    "INPUT_VALIDATION_FAILED": "⛔ Source XML validation failed",
}


def main():
    """Main entry point for the outputs import script."""

    print_logo()

    configure_logging()
    args = _parse_args()
    outputs_import(
        xml_dir=args.xml_dir,
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        processes=args.processes,
        apply=args.apply,
        limit=args.limit,
        binaries=args.binaries,
        pids=args.pids.split(",") if args.pids else None,
        fedora_url=args.fedora_url or "",
        cora_url=args.cora_url,
    )


def outputs_import(
    xml_dir: str,
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
    apply: bool,
    limit: int | None = None,
    binaries: bool = False,
    pids: list[str] | None = None,
    fedora_url: str = "",
    cora_url: str | None = None,
):
    start_time = time.perf_counter()

    source_records = _read_source_records(xml_dir, limit)

    if pids is not None:
        source_records = [
            record for record in source_records if record.findtext("pid") in pids
        ]

    print(f"Starting migration of {len(source_records)} records to {system} system...")
    counts = {
        "SUCCESS": 0,
        "CLASSIC_QUALITY": 0,
        "FAILED": 0,
        "SKIPPED": 0,
        "INPUT_VALIDATION_FAILED": 0,
    }
    results = []
    with Pool(
        processes,
        _init_context,
        initargs=(
            system,
            login_id,
            app_token,
            apply,
            binaries,
            fedora_url,
            cora_url,
        ),
    ) as pool, tqdm(total=len(source_records), desc="Importing records") as progress:
        for result in pool.imap_unordered(_migrate_record, source_records):
            counts[result.status] += 1
            results.append(result)
            progress.set_postfix_str(
                f"✅ {counts['SUCCESS']} | ⚠️ {counts['CLASSIC_QUALITY']} | ❌ {counts['FAILED']} | ➡️ {counts['SKIPPED']} | ⛔{counts['INPUT_VALIDATION_FAILED']}"
            )
            progress.update(1)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Migration completed in {elapsed_time:.2f} seconds.")

    _save_reports(results, xml_dir=xml_dir, system=system, output_dir="reports")


def _save_reports(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    _save_html_report(results, xml_dir=xml_dir, system=system, output_dir=output_dir)
    _save_markdown_report(
        results, xml_dir=xml_dir, system=system, output_dir=output_dir
    )
    _print_rich_report(results)


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            "--xml-dir": {
                "help": "Directory containing XML files to process",
                "required": True,
            },
            **cora_url_argument,
            **classic_arguments,
            "--system": {
                "default": "pre",
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--processes": {
                "type": int,
                "default": 2,
                "help": "Number of processes",
            },
            "--apply": {
                "action": "store_true",
                "help": "Create records in Cora. (If not set, will behave as a dry-run)",
            },
            "--limit": {
                "type": int,
                "help": "Limit the number of processed files (for testing purposes)",
                "default": None,
            },
            "--binaries": {
                "action": "store_true",
                "help": "Also migrate binaries associated with the publications",
                "default": False,
            },
            "--pids": {
                "help": "Comma-separated list of PIDs to process (for testing purposes)",
            },
        },
    )

    return parser.parse_args()


def _init_context(
    system, login_id, app_token, apply_flag, binaries_flag, fedora_url_arg, cora_url
):
    global context, apply, with_binaries, fedora_url
    configure_logging()
    context = CoraContext(
        system=system,
        login_id=login_id,
        app_token=app_token,
        cora_url=cora_url,
    )
    apply = apply_flag
    with_binaries = binaries_flag
    fedora_url = fedora_url_arg


def _migrate_record(source_record):
    assert context is not None, "Context must be initialized before migrating records"
    return output_migrate(
        source_record,
        context,
        apply,
        with_binaries=with_binaries,
        fedora_url=fedora_url,
    )


def _read_source_records(xml_dir: str, limit: int | None = None) -> list[ET.Element]:
    records = [
        read_source_xml(os.path.join(xml_dir, filename))
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]
    if limit is not None:
        return records[:limit]
    return records


def _generate_report(results: list[OutputMigrationResult]):
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


def _print_rich_report(results: list[OutputMigrationResult]):
    """Prints the output of _generate_report using a table from the rich library."""
    console = Console()
    status_counts, errors = _generate_report(results)

    # Print status counts table
    table = Table(title="Migration Status Counts")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    for status, count in status_counts.items():
        table.add_row(status, str(count))
    console.print(table)

    # Print errors by category
    for category in ["INPUT_VALIDATION_FAILED", "FAILED", "CLASSIC_QUALITY", "SKIPPED"]:
        if errors.get(category):
            error_dict = errors[category]
            if error_dict:
                error_table = Table(title=f"{category} Errors", show_lines=True)
                error_table.add_column("Error Message", style="red")
                error_table.add_column("Occurrences", justify="right")
                error_table.add_column("PIDs", style="cyan")
                for error_msg, pids in error_dict.items():
                    error_table.add_row(error_msg, str(len(pids)), ", ".join(pids))
                console.print(error_table)


def _generate_setup_for_report(
    xml_dir: str, output_dir: str = ".", filetype: str = "md"
):
    domain_match = re.search(r"fedora_xml/(.+)/.+", xml_dir)
    domain = domain_match.group(1) if domain_match else "unknown"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    filename = f"outputs-import-{domain}-{timestamp}.{filetype}"
    filepath = os.path.join(output_dir, filename)
    return (domain, timestamp, filepath)


def _save_markdown_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    status_counts, errors = _generate_report(results)
    domain, timestamp, filepath = _generate_setup_for_report(xml_dir, output_dir, "md")

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
        lines.append(f"| {status_labels[status]} | {count} |")
    lines.append("")

    for category in ["INPUT_VALIDATION_FAILED", "FAILED", "CLASSIC_QUALITY", "SKIPPED"]:
        error_dict = errors.get(category, {})
        if error_dict:
            lines.append(f"## {status_labels[category]}\n")
            lines.append("| Error Message | Occurrences | PIDs |")
            lines.append("|--------------|-------------|------|")
            for error_msg, pids in error_dict.items():
                pid_str = ", ".join(pids)
                lines.append(
                    f"| {error_msg.replace('|', ' ').replace(chr(10), ' ')} | {len(pids)} | {pid_str} |"
                )
            lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Markdown report saved to {filepath}")


def _save_html_report(
    results: list[OutputMigrationResult],
    xml_dir: str,
    system: str,
    output_dir: str = ".",
):
    status_counts, errors = _generate_report(results)
    domain, timestamp, filepath = _generate_setup_for_report(
        xml_dir, output_dir, "html"
    )

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
        td1.text = status_labels[status]
        td2 = ET.SubElement(tr, "td")
        td2.text = str(count)

    for category in ["INPUT_VALIDATION_FAILED", "FAILED", "CLASSIC_QUALITY", "SKIPPED"]:
        error_dict = errors.get(category, {})
        if error_dict:
            h2 = ET.SubElement(body, "h2")
            h2.text = f"{status_labels[category]}"
            table = ET.SubElement(body, "table")
            tr_head = ET.SubElement(table, "tr")
            for col in ["Error Message", "Occurrences", "PIDs"]:
                th = ET.SubElement(tr_head, "th")
                th.text = col
            for error_msg, pids in error_dict.items():
                tr = ET.SubElement(table, "tr")
                td1 = ET.SubElement(tr, "td")
                td1.text = error_msg.replace("|", " ").replace("\n", " ")
                td2 = ET.SubElement(tr, "td")
                td2.text = str(len(pids))
                td3 = ET.SubElement(tr, "td")
                td3.text = ", ".join(pids)

    html_str = ET.tostring(html, encoding="unicode", method="html")
    doctype = "<!DOCTYPE html>\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doctype + html_str)
    print(f"HTML report saved to {filepath}")


if __name__ == "__main__":
    main()
