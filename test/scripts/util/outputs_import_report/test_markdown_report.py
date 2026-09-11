from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts.util.outputs_import_report.markdown_report import save_markdown_report


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
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        output_dir=str(tmp_path),
    )

    report_files = list(tmp_path.glob("outputs-import-umu-*.md"))
    assert len(report_files) == 1

    report_text = report_files[0].read_text(encoding="utf-8")

    assert "# Migration Report (" in report_text
    assert "**Total records processed:** 4" in report_text
    assert "**Domain: umu | Target System:** `pre`" in report_text
    assert "✅ Successfully imported as data quality DiVA 2026" in report_text
    assert "⚠️ Validation errors (imported as classic data quality)" in report_text
    assert "❌ Failed to import" in report_text
    assert "⛔ Source XML validation failed" in report_text

    sanitized_error = "bad | error\nline".replace("|", " ").replace("\n", " ")
    assert sanitized_error in report_text
    assert "book: pid-2" in report_text
