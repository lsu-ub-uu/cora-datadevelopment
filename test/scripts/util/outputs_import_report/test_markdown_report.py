from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
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
