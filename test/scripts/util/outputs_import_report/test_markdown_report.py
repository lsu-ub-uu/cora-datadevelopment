import pytest
from html.parser import HTMLParser

from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from fedora_to_cora.person_migrate import MigratePersonResult
from fedora_to_cora.persons_migrate import (
    PersonMigrationOutcome,
    PersonMigrationSummary,
)
from scripts.util.outputs_import_report.markdown_report import save_markdown_report
from scripts.util.outputs_import_report.save_reports import save_reports


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.in_table = False
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.tables.append([])
        elif self.in_table and tag == "tr":
            self.tables[-1].append([])
        elif self.in_table and tag in ("th", "td"):
            self.in_cell = True
            self.tables[-1][-1].append("")

    def handle_data(self, data):
        if self.in_cell:
            self.tables[-1][-1][-1] += data

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag in ("th", "td"):
            self.in_cell = False


@pytest.mark.parametrize(
    "person_mode", ["not_requested", "empty", "outcomes", "errors"]
)
def test_both_reports_start_with_separate_migration_summary_tables(
    tmp_path, person_mode
):
    summary = None if person_mode == "not_requested" else PersonMigrationSummary()
    if person_mode == "outcomes":
        summary.outcomes = [
            PersonMigrationOutcome(
                "person:1", MigratePersonResult("CREATED", "1", None)
            ),
            PersonMigrationOutcome(
                "person:2", MigratePersonResult("SKIPPED", None, None)
            ),
            PersonMigrationOutcome(
                "person:3", MigratePersonResult("FAILED", None, "Rejected")
            ),
        ]
    elif person_mode == "errors":
        summary.xml_files = 1
        summary.scan_errors = {"broken.xml": "Invalid XML"}
        summary.initialization_error = "Login failed"
    relations = [
        OutputRelationMigrationResult(
            status=status, pid=f"pid:{number}", cora_id=None, error=None
        )
        for number, status in enumerate(
            ("UPDATED", "UPDATED", "NO_RELATIONS", "FAILED")
        )
    ]

    save_reports(
        [
            OutputMigrationResult("pid:1", "article", status="SUCCESS"),
            OutputMigrationResult(
                "pid:skipped",
                "article",
                status="SKIPPED",
                errors=["Record already exists in target system"],
            ),
        ],
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        apply=True,
        binaries=False,
        cora_url=None,
        output_dir=str(tmp_path),
        relation_results=relations,
        person_summary=summary,
    )

    expected = {
        "Outputs": [
            ["Status", "Count"],
            ["✅ Successfully imported as data quality DiVA 2026", "1"],
            ["⚠️ Validation errors (imported as classic data quality)", "0"],
            ["❌ Failed to import", "0"],
            ["➡️ Skipped (record already migrated)", "1"],
            ["⛔ Source XML validation failed", "0"],
        ]
    }
    if summary is not None:
        count = "1" if person_mode == "outcomes" else "0"
        expected["Persons"] = [
            ["Status", "Count"],
            ["✅ Created", count],
            ["➡️ Skipped", count],
            ["❌ Failed", count],
        ]
    expected["Output relations"] = [
        ["Status", "Count"],
        ["✅ Updated", "2"],
        ["➡️ No relations", "1"],
        ["❌ Failed", "1"],
    ]

    markdown = next(tmp_path.glob("*.md")).read_text()
    assert "Record already exists in target system" not in markdown
    assert "## ➡️ Skipped" not in markdown
    assert "## Status Counts" not in markdown
    assert "| Migration |" not in markdown
    summary_section = markdown.split("## Summary\n", 1)[1].split("\n## ", 1)[0]
    sections = summary_section.split("### ")[1:]
    assert len(sections) == len(expected)
    for section, (title, expected_rows) in zip(sections, expected.items()):
        assert section.splitlines()[0] == title
        rows = [
            [cell.strip() for cell in line.strip("|").split("|")]
            for line in section.splitlines()
            if line.startswith("|")
        ]
        assert [rows[0], *rows[2:]] == expected_rows
    html = next(tmp_path.glob("*.html")).read_text()
    assert "Record already exists in target system" not in html
    assert "<h2>➡️ Skipped" not in html
    assert "<h2>Summary</h2>" in html
    assert "Status Counts" not in html
    assert "<th>Migration</th>" not in html
    for title in expected:
        assert f"<h3>{title}</h3>" in html
    parser = _TableParser()
    parser.feed(html)
    assert parser.tables[: len(expected)] == list(expected.values())
    if summary is not None:
        assert parser.tables[len(expected)][1:] == expected["Persons"][1:]


def test_save_markdown_report_creates_expected_file(tmp_path):
    results = [
        OutputMigrationResult("pid-1", "article", status="SUCCESS"),
        OutputMigrationResult(
            "pid-2",
            "book",
            status="FAILED",
            errors=["bad | error\nline"],
        ),
        OutputMigrationResult(
            "pid-3",
            "conferencePaper",
            status="CLASSIC_QUALITY",
            errors=["classic issue"],
        ),
        OutputMigrationResult(
            "pid-4",
            "thesis",
            status="INPUT_VALIDATION_FAILED",
            errors=["invalid source xml"],
        ),
    ]

    save_markdown_report(
        results,
        xml_dir="data/fedora_xml/umu/2026-09-21T14:37:18.299640",
        system="pre",
        apply=False,
        binaries=False,
        cora_url=None,
        output_dir=str(tmp_path),
    )

    report_files = list(tmp_path.glob("outputs-import-umu-*.md"))
    assert len(report_files) == 1

    report_text = report_files[0].read_text(encoding="utf-8")

    assert "# Migration Report (" in report_text
    assert "**Total records processed:** 4" in report_text
    assert "**Export date:** `2026-09-21T14:37:18.299640`" in report_text
    assert "data/fedora_xml" not in report_text
    assert "**Domain:** umu" in report_text
    assert "**Target system:** `pre`" in report_text
    assert "**Dry run:** Yes" in report_text
    assert "**With binaries:** No" in report_text
    assert "✅ Successfully imported as data quality DiVA 2026" in report_text
    assert "⚠️ Validation errors (imported as classic data quality)" in report_text
    assert "❌ Failed to import" in report_text
    assert "⛔ Source XML validation failed" in report_text

    sanitized_error = "bad | error\nline".replace("|", " ").replace("\n", " ")
    assert sanitized_error in report_text
    assert "book: pid-2" in report_text
    assert "Failed to migrate relations" not in report_text
    assert "Person Migration" not in report_text


def test_save_markdown_report_includes_relation_errors_section(tmp_path):
    results = [OutputMigrationResult("pid-1", "article", status="SUCCESS")]
    relation_results = [
        OutputRelationMigrationResult(
            status="UPDATED", pid="pid-1", cora_id="1", error=None
        ),
        OutputRelationMigrationResult(
            status="FAILED", pid="pid-2", cora_id="2", error="bad | rel\nissue"
        ),
        OutputRelationMigrationResult(
            status="FAILED", pid="pid-3", cora_id="3", error="bad | rel\nissue"
        ),
    ]

    save_markdown_report(
        results,
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        apply=True,
        binaries=True,
        cora_url=None,
        output_dir=str(tmp_path),
        relation_results=relation_results,
    )

    report_text = next(tmp_path.glob("outputs-import-umu-*.md")).read_text(
        encoding="utf-8"
    )

    sanitized = "bad | rel\nissue".replace("|", " ").replace("\n", " ")
    assert "## ❌ Failed to migrate relations" in report_text
    assert sanitized in report_text
    assert "pid-2, pid-3" in report_text


@pytest.mark.parametrize("mode", ["empty", "success", "failed", "scan", "auth"])
def test_both_reports_include_person_migration(tmp_path, mode):
    summary = PersonMigrationSummary()
    if mode == "success":
        summary.xml_files = 2
        summary.unique_persons = 2
        summary.outcomes = [
            PersonMigrationOutcome(
                "person:1", MigratePersonResult("CREATED", "1", None)
            ),
            PersonMigrationOutcome(
                "person:2", MigratePersonResult("SKIPPED", None, "Exists")
            ),
        ]
    elif mode == "failed":
        summary.outcomes = [
            PersonMigrationOutcome(
                pid, MigratePersonResult("FAILED", None, "bad | error\n<detail>")
            )
            for pid in ("person:2", "person:1")
        ]
        summary.outcomes.append(
            PersonMigrationOutcome(
                "person:3", MigratePersonResult("FAILED", None, None)
            )
        )
    elif mode == "scan":
        summary.xml_files = 1
        summary.scan_errors = {"broken.xml": "Invalid <xml>"}
    elif mode == "auth":
        summary.unique_persons = 1
        summary.initialization_error = "Login <failed>"

    save_reports(
        [],
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        apply=True,
        binaries=False,
        cora_url=None,
        output_dir=str(tmp_path),
        person_summary=summary,
    )

    for extension in ("html", "md"):
        text = next(tmp_path.glob(f"*.{extension}")).read_text()
        assert "Person Migration" in text
        assert "Unique persons" not in text
        assert "XML files read" not in text
        assert "XML files failed" not in text
        assert "Initialization failures" not in text
        assert "| XML files |" not in text
        assert "<td>XML files</td>" not in text
        assert "Created" in text
        assert "Skipped" in text
        assert "Failed" in text
        notice = "Person migration encountered errors; output and relation migration continued."
        assert (notice in text) == summary.has_failures
        assert "Output and relation migration not run" not in text
        if mode == "failed":
            assert "person:1, person:2" in text
            assert "Unknown error" in text
            assert "bad   error " in text
            assert "&lt;detail&gt;" in text
        elif mode == "scan":
            assert "broken.xml" in text
            assert "Invalid" in text
        elif mode == "auth":
            assert "Login" in text
