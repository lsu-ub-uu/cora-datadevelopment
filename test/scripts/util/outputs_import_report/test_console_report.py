from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.console_report import print_console_report


def test_print_console_report_outputs_summary_only(capsys):
    results = [
        OutputMigrationResult("pid-1", "article", status="SUCCESS"),
        OutputMigrationResult(
            "pid-2",
            "book",
            status="FAILED",
            errors=["failed issue"],
        ),
        OutputMigrationResult(
            "pid-3",
            "conferencePaper",
            status="CLASSIC_QUALITY",
            errors=["classic issue"],
        ),
    ]

    print_console_report(
        results,
        xml_dir="data/fedora_xml/umu/2026-09-21T14:37:18.299640",
        system="pre",
        apply=False,
        binaries=True,
        cora_url=None,
    )

    captured = capsys.readouterr()
    output = captured.out

    assert "==== Migration Report ====" in output
    assert "Total records processed: 3" in output
    assert "Migration Status Counts" in output
    assert "Export date: 2026-09-21T14:37:18.299640" in output
    assert "Target system: pre" in output
    assert "Dry run: Yes" in output
    assert "With binaries: Yes" in output
    assert "FAILED Errors" not in output
    assert "CLASSIC_QUALITY Errors" not in output
    assert "failed issue" not in output
    assert "classic issue" not in output
    assert "book: pid-2" not in output


def test_print_console_report_omits_relation_errors_section(capsys):
    results = [OutputMigrationResult("pid-1", "article", status="SUCCESS")]
    relation_results = [
        OutputRelationMigrationResult(
            status="UPDATED", pid="pid-1", cora_id="1", error=None
        ),
        OutputRelationMigrationResult(
            status="FAILED", pid="pid-2", cora_id="2", error="boom"
        ),
    ]

    print_console_report(
        results,
        xml_dir="data/fedora_xml/umu/outputs",
        system="pre",
        apply=True,
        binaries=False,
        cora_url="https://cora.example.org",
        relation_results=relation_results,
    )

    output = capsys.readouterr().out

    assert "Target system: https://cora.example.org" in output
    assert "Failed to migrate relations" not in output
    assert "boom" not in output
    assert "pid-2" not in output
