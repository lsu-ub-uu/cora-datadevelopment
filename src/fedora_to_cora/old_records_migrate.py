import logging
from collections import Counter
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from common.common_data import read_source_xml
from common.environment import load_environment
from common.logging_config import configure_logging
from common.threads import run_with_threads
from cora.context import Context, CoraContext
from fedora_to_cora.migrate_old_record import MigrateOldRecordResult, old_record_migrate

logger = logging.getLogger(__name__)


@dataclass
class OldRecordMigrationOutcome:
    xml_path: Path
    result: MigrateOldRecordResult

    @property
    def status(self) -> str:
        return self.result.status

    @property
    def error(self) -> str | None:
        return self.result.error


@dataclass
class OldRecordMigrationSummary:
    xml_files: int = 0
    outcomes: list[OldRecordMigrationOutcome] = field(default_factory=list)
    initialization_error: str | None = None

    @property
    def counts(self) -> dict[str, int]:
        counts = Counter(outcome.status for outcome in self.outcomes)
        return {status: counts[status] for status in ("CREATED", "SKIPPED", "FAILED")}


def _migrate_old_record(xml_path: Path, context: Context) -> OldRecordMigrationOutcome:
    try:
        source_record = read_source_xml(xml_path)
        result = old_record_migrate(source_record, context)
    except Exception as error:
        result = MigrateOldRecordResult("FAILED", None, str(error))
    if result.status == "FAILED":
        logger.error("Failed to migrate old record %s: %s", xml_path, result.error)
    return OldRecordMigrationOutcome(xml_path, result)


def migrate_old_records(
    xml_dir: Path,
    system: str | None = None,
    login_id: str | None = None,
    app_token: str | None = None,
    workers: int = 1,
    cora_url: str | None = None,
) -> OldRecordMigrationSummary:
    if not xml_dir.is_dir():
        raise ValueError(f"Not a directory: {xml_dir}")
    if workers < 1:
        raise ValueError("Workers must be a positive integer")
    xml_files = sorted(path for path in xml_dir.glob("*.xml") if path.is_file())
    summary = OldRecordMigrationSummary(xml_files=len(xml_files))
    if not xml_files:
        return summary
    try:
        context = CoraContext(
            system=system,
            login_id=login_id,
            app_token=app_token,
            workers=workers,
            cora_url=cora_url,
        )
    except Exception as error:
        logger.error("Failed to initialize old-record migration context: %s", error)
        summary.initialization_error = str(error)
        return summary
    summary.outcomes = run_with_threads(
        xml_files,
        partial(_migrate_old_record, context=context),
        workers=workers,
        desc="Migrating old records",
        status_order=[
            ("CREATED", "\u2705"),
            ("SKIPPED", "\u27a1\ufe0f"),
            ("FAILED", "\u274c"),
        ],
    )
    logger.info("Old-record migration completed: %s", summary.counts)
    return summary


if __name__ == "__main__":
    load_environment()
    configure_logging()
    migrate_old_records(
        xml_dir=Path("data/fedora_xml/uu/2025-10-31T09:06:10.939513"),
        cora_url="https://preview.diva.cora.epc.ub.uu.se",
        workers=1,
    )
