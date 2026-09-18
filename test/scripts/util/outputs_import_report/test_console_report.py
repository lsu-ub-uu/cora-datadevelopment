from fedora_to_cora.output_migrate import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import OutputRelationMigrationResult
from scripts.util.outputs_import_report.console_report import print_console_report


def test_print_console_report_outputs_summary_and_error_tables(capsys):
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

    print_console_report(results)

    captured = capsys.readouterr()
    output = captured.out

    assert "==== Migration Report ====" in output
    assert "Total records processed: 3" in output
    assert "Migration Status Counts" in output
    assert "FAILED Errors" in output
    assert "CLASSIC_QUALITY Errors" in output
    assert "failed issue" in output
    assert "book: pid-2" in output


def test_print_console_report_renders_relation_errors_section(capsys):
    results = [OutputMigrationResult("pid-1", "article", status="SUCCESS")]
    relation_results = [
        OutputRelationMigrationResult(
            status="UPDATED", pid="pid-1", cora_id="1", error=None
        ),
        OutputRelationMigrationResult(
            status="FAILED", pid="pid-2", cora_id="2", error="boom"
        ),
        OutputRelationMigrationResult(
            status="FAILED", pid="pid-3", cora_id="3", error="boom"
        ),
    ]

    print_console_report(results, relation_results=relation_results)

    output = capsys.readouterr().out

    assert "Failed to migrate relations" in output
    assert "boom" in output
    assert "pid-2" in output
    assert "pid-3" in output


def test_print_console_report_omits_relation_errors_when_none(capsys):
    results = [OutputMigrationResult("pid-1", "article", status="SUCCESS")]
    relation_results = [
        OutputRelationMigrationResult(
            status="UPDATED", pid="pid-1", cora_id="1", error=None
        ),
    ]

    print_console_report(results, relation_results=relation_results)

    assert "Failed to migrate relations" not in capsys.readouterr().out
