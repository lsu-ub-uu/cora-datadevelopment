from fedora_to_cora.output_migrate import OutputMigrationResult
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
