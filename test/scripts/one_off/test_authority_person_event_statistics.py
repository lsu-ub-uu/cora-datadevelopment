from datetime import date

from scripts.one_off.CORA_3879_get_person_statistics.authority_person_event_statistics import (
    aggregate_events,
    format_report,
    write_html_report,
)


def test_aggregate_events_counts_create_and_update_by_month(tmp_path):
    xml_path = tmp_path / "synthetic.xml"
    xml_path.write_text(
        """
        <authorityPerson>
          <pid>synthetic-person-id</pid>
          <recordInfo>
            <events>
              <event><type>CREATE</type><timestamp>2026-01-03T08:00:00Z</timestamp></event>
              <event><type>UPDATE</type><timestamp>2026-01-03T09:00:00Z</timestamp></event>
              <event><type>UPDATE</type><timestamp>2026-01-31T23:59:59-08:00</timestamp></event>
              <event><type>CREATE</type><timestamp>2026-02-01T00:00:00Z</timestamp></event>
              <event><type>DELETE</type><timestamp>2026-02-02T00:00:00Z</timestamp></event>
              <event><type>UPDATE</type><timestamp>2025-12-31T23:59:59Z</timestamp></event>
              <event><type>UPDATE</type><timestamp>2026-11-06T00:00:00Z</timestamp></event>
            </events>
          </recordInfo>
          <metadata>
            <recordInfo>
              <events>
                <event><type>CREATE</type><timestamp>2026-05-01T00:00:00Z</timestamp></event>
              </events>
            </recordInfo>
          </metadata>
        </authorityPerson>
        """,
        encoding="utf-8",
    )

    counts, malformed_file_count, invalid_event_count = aggregate_events([xml_path])

    assert counts[(2025, 12)] == {"CREATE": 0, "UPDATE": 1}
    assert counts[(2026, 1)] == {"CREATE": 1, "UPDATE": 2}
    assert counts[(2026, 2)] == {"CREATE": 1, "UPDATE": 0}
    assert counts[(2026, 11)] == {"CREATE": 0, "UPDATE": 1}
    assert malformed_file_count == 0
    assert invalid_event_count == 0


def test_aggregate_events_counts_malformed_files_and_invalid_events(tmp_path):
    malformed_path = tmp_path / "malformed.xml"
    malformed_path.write_text("<authorityPerson>", encoding="utf-8")
    valid_path = tmp_path / "valid.xml"
    valid_path.write_text(
        """
        <authorityPerson>
          <recordInfo>
            <events>
              <event><type>CREATE</type></event>
              <event><type>UPDATE</type><timestamp>not-a-timestamp</timestamp></event>
              <event><type>DELETE</type></event>
            </events>
          </recordInfo>
        </authorityPerson>
        """,
        encoding="utf-8",
    )

    counts, malformed_file_count, invalid_event_count = aggregate_events(
        [malformed_path, valid_path]
    )

    assert all(
        value == 0
        for month_counts in counts.values()
        for value in month_counts.values()
    )
    assert malformed_file_count == 1
    assert invalid_event_count == 2


def test_format_report_limits_months_and_exposes_only_aggregate_data():
    counts = {
        (2025, 12): {"CREATE": 1, "UPDATE": 0},
        (2026, 2): {"CREATE": 0, "UPDATE": 1},
    }

    report = format_report(
        counts,
        malformed_file_count=2,
        invalid_event_count=3,
    )

    assert "2025-12  CREATE 1  UPDATE 0" in report
    assert "2026-01  CREATE 0  UPDATE 0" in report
    assert "2026-02  CREATE 0  UPDATE 1" in report
    assert "Malformed or unreadable files: 2" in report
    assert "Invalid or missing event timestamps: 3" in report
    assert "synthetic-person-id" not in report
    assert "2026-01-03T08:00:00Z" not in report


def test_write_html_report_saves_aggregate_monthly_table(tmp_path):
    counts = {
        (2025, 12): {"CREATE": 1, "UPDATE": 0},
        (2026, 2): {"CREATE": 0, "UPDATE": 1},
    }

    report_path = write_html_report(
        counts,
        malformed_file_count=2,
        invalid_event_count=3,
        output_dir=tmp_path,
    )

    report = report_path.read_text(encoding="utf-8")
    assert report_path.name.startswith("authority-person-event-statistics-all-years-")
    assert report.startswith("<!DOCTYPE html>")
    assert "Monthly authority person event counts across all years" in report
    assert "2025-12" in report
    assert "2026-01" in report
    assert "2026-02" in report
    assert "Malformed or unreadable files: 2" in report
    assert "Invalid or missing event timestamps: 3" in report
    assert "synthetic-person-id" not in report
    assert "2026-01-03T08:00:00Z" not in report
