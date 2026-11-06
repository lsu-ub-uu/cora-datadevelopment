from collections.abc import Iterable
from datetime import date, datetime
from functools import partial
from pathlib import Path
import xml.etree.ElementTree as ET

from common.threads import run_with_threads

EVENT_TYPES = ("CREATE", "UPDATE", "DELETE")
DEFAULT_XML_DIRECTORY = Path("data/fedora/authority_person_xml")


def main() -> None:
    if not DEFAULT_XML_DIRECTORY.is_dir():
        raise SystemExit("Authority person XML directory does not exist")

    monthly_counts, malformed_file_count, invalid_event_count = _aggregate_events(
        DEFAULT_XML_DIRECTORY.glob("*.xml")
    )
    report_arguments = (
        monthly_counts,
        malformed_file_count,
        invalid_event_count,
    )
    print(_format_report(*report_arguments))
    html_report_path = _write_html_report(*report_arguments)
    print(f"HTML report saved to {html_report_path}")


def _aggregate_events(
    xml_paths: Iterable[Path],
) -> tuple[dict[tuple[int, int], dict[str, int]], int, int]:
    file_results = run_with_threads(
        list(xml_paths),
        _aggregate_file_events,
        desc="Reading authority person XMLs",
        workers=32,
    )
    monthly_counts: dict[tuple[int, int], dict[str, int]] = {}
    malformed_file_count = 0
    invalid_event_count = 0
    for file_counts, file_malformed_count, file_invalid_event_count in file_results:
        malformed_file_count += file_malformed_count
        invalid_event_count += file_invalid_event_count
        for year_month, event_counts in file_counts.items():
            month_counts = monthly_counts.setdefault(
                year_month, {event_type: 0 for event_type in EVENT_TYPES}
            )
            for event_type, count in event_counts.items():
                month_counts[event_type] += count

    return monthly_counts, malformed_file_count, invalid_event_count


def _aggregate_file_events(
    xml_path: Path,
) -> tuple[dict[tuple[int, int], dict[str, int]], int, int]:
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError):
        return {}, 1, 0

    record_info = root.find("./recordInfo")
    if record_info is None:
        return {}, 0, 0

    events = record_info.find("./events")
    if events is None:
        return {}, 0, 0

    monthly_counts: dict[tuple[int, int], dict[str, int]] = {}
    invalid_event_count = 0
    for event in events.findall("./event"):
        event_type = _child_text(event, "type")
        if event_type not in EVENT_TYPES:
            continue

        timestamp_text = _child_text(event, "timestamp")
        if timestamp_text is None:
            invalid_event_count += 1
            continue
        try:
            timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
        except ValueError:
            invalid_event_count += 1
            continue

        year_month = (timestamp.year, timestamp.month)
        event_counts = monthly_counts.setdefault(
            year_month, {event_type: 0 for event_type in EVENT_TYPES}
        )
        event_counts[event_type] += 1

    return monthly_counts, 0, invalid_event_count


def _format_report(
    monthly_counts: dict[tuple[int, int], dict[str, int]],
    malformed_file_count: int,
    invalid_event_count: int,
) -> str:
    lines = [
        "Monthly authority person event counts across all years",
        "Month     CREATE  UPDATE  DELETE",
    ]
    for year, month in _iter_months(monthly_counts):
        counts = monthly_counts.get(
            (year, month), {event_type: 0 for event_type in EVENT_TYPES}
        )
        lines.append(
            f"{year}-{month:02d}  CREATE {counts['CREATE']}  UPDATE {counts['UPDATE']}  DELETE {counts['DELETE']}"
        )
    lines.extend(
        [
            f"Malformed or unreadable files: {malformed_file_count}",
            f"Invalid or missing event timestamps: {invalid_event_count}",
        ]
    )
    return "\n".join(lines)


def _write_html_report(
    monthly_counts: dict[tuple[int, int], dict[str, int]],
    malformed_file_count: int,
    invalid_event_count: int,
    output_dir: Path = Path("reports"),
) -> Path:
    html = ET.Element("html")
    head = ET.SubElement(html, "head")
    ET.SubElement(head, "title").text = "Authority Person Event Counts (All Years)"
    ET.SubElement(head, "meta", attrib={"charset": "utf-8"})
    ET.SubElement(head, "style").text = (
        "body{font-family:sans-serif;max-width:900px;margin:2em auto;}"
        "table{border-collapse:collapse;margin:1em 0;}"
        "th,td{border:1px solid #ccc;padding:6px 12px;text-align:left;}"
        "th{background:#e8edf2;}"
    )

    body = ET.SubElement(html, "body")
    ET.SubElement(body, "h1").text = (
        "Monthly authority person event counts across all years"
    )
    table = ET.SubElement(body, "table")
    header = ET.SubElement(table, "tr")
    for label in ("Month", "CREATE", "UPDATE", "DELETE"):
        ET.SubElement(header, "th").text = label
    for year, month in _iter_months(monthly_counts):
        counts = monthly_counts.get(
            (year, month), {event_type: 0 for event_type in EVENT_TYPES}
        )
        row = ET.SubElement(table, "tr")
        ET.SubElement(row, "td").text = f"{year}-{month:02d}"
        ET.SubElement(row, "td").text = str(counts["CREATE"])
        ET.SubElement(row, "td").text = str(counts["UPDATE"])
        ET.SubElement(row, "td").text = str(counts["DELETE"])

    ET.SubElement(body, "p").text = (
        f"Malformed or unreadable files: {malformed_file_count}"
    )
    ET.SubElement(body, "p").text = (
        f"Invalid or missing event timestamps: {invalid_event_count}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report_date = date.today()
    report_path = output_dir / (
        f"authority-person-event-statistics-all-years-{report_date:%Y-%m-%d}.html"
    )
    html_content = "<!DOCTYPE html>\n" + ET.tostring(
        html, encoding="unicode", method="html"
    )
    report_path.write_text(html_content, encoding="utf-8")
    return report_path


def _iter_months(
    monthly_counts: dict[tuple[int, int], dict[str, int]],
) -> Iterable[tuple[int, int]]:
    if not monthly_counts:
        return

    year, month = min(monthly_counts)
    last_year, last_month = max(monthly_counts)
    while (year, month) <= (last_year, last_month):
        yield year, month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def _child_text(element: ET.Element, child_name: str) -> str | None:
    text = element.findtext(f"./{child_name}")
    return text.strip() if text else None


if __name__ == "__main__":
    main()
