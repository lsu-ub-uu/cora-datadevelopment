from fedora_to_cora.output_migrate import OutputMigrationResult
from scripts.util.outputs_import_report.html_report import save_html_report


def test_save_html_report_creates_expected_file(tmp_path):
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
            status="SKIPPED",
            errors=["already exists"],
        ),
    ]

    save_html_report(
        results,
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        output_dir=str(tmp_path),
    )

    report_files = list(tmp_path.glob("outputs-import-umu-*.html"))
    assert len(report_files) == 1

    report_text = report_files[0].read_text(encoding="utf-8")

    assert report_text.startswith("<!DOCTYPE html>")
    assert "Migration Report (" in report_text
    assert "Total records processed: 3" in report_text
    assert "Domain: umu | Target System: pre" in report_text
    assert "✅ Successfully imported as data quality DiVA 2026" in report_text
    assert "❌ Failed to import" in report_text
    assert "➡️ Skipped" in report_text

    sanitized_error = "bad | error\nline".replace("|", " ").replace("\n", " ")
    assert sanitized_error in report_text
    assert "<strong>book: </strong>pid-2" in report_text
