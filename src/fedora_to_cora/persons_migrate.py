import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
import xml.etree.ElementTree as ET

from common.common_data import read_source_xml
from common.threads import run_with_threads
from cora.context import Context, CoraContext
from fedora_to_cora.person_migrate import MigratePersonResult, migrate_person

logger = logging.getLogger(__name__)


@dataclass
class PersonMigrationOutcome:
    authority_pid: str
    result: MigratePersonResult

    @property
    def status(self) -> str:
        return self.result.status

    @property
    def error(self) -> str | None:
        return self.result.error


@dataclass
class PersonMigrationSummary:
    xml_files: int = 0
    unique_persons: int = 0
    outcomes: list[PersonMigrationOutcome] = field(default_factory=list)
    scan_errors: dict[str, str] = field(default_factory=dict)
    initialization_error: str | None = None

    @property
    def files_read(self) -> int:
        return self.xml_files - len(self.scan_errors)

    @property
    def counts(self) -> dict[str, int]:
        counts = Counter(outcome.status for outcome in self.outcomes)
        return {status: counts[status] for status in ("CREATED", "SKIPPED", "FAILED")}

    @property
    def has_failures(self) -> bool:
        return bool(
            self.scan_errors
            or self.initialization_error is not None
            or self.counts["FAILED"]
        )

    @property
    def errors(self) -> dict[str, list[str]]:
        errors: dict[str, list[str]] = defaultdict(list)
        for outcome in self.outcomes:
            if outcome.status == "FAILED":
                errors[outcome.error or "Unknown error"].append(outcome.authority_pid)
        return {
            error: sorted(pids)
            for error, pids in sorted(
                errors.items(), key=lambda item: (-len(item[1]), item[0])
            )
        }


def _read_authority_pids(xml_path: Path) -> tuple[Path, set[str], str | None]:
    try:
        publication = read_source_xml(xml_path)
    except (ET.ParseError, OSError) as error:
        logger.error("Failed to read %s: %s", xml_path, error)
        return xml_path, set(), str(error)
    authority_pids = {
        element.text.strip()
        for element in publication.findall(".//authorityPid")
        if element.text and element.text.strip()
    }
    return xml_path, authority_pids, None


def _migrate_person(authority_pid: str, context: Context) -> PersonMigrationOutcome:
    try:
        result = migrate_person(authority_pid, context)
    except Exception as error:
        result = MigratePersonResult("FAILED", None, str(error))
    if result.status == "FAILED":
        logger.error("Failed to migrate %s: %s", authority_pid, result.error)
    return PersonMigrationOutcome(authority_pid, result)


def migrate_persons(
    xml_dir: Path,
    system: str | None = None,
    login_id: str | None = None,
    app_token: str | None = None,
    workers: int = 1,
    cora_url: str | None = None,
) -> PersonMigrationSummary:
    if not xml_dir.is_dir():
        raise ValueError(f"Not a directory: {xml_dir}")
    if workers < 1:
        raise ValueError("Workers must be a positive integer")
    xml_files = sorted(path for path in xml_dir.glob("*.xml") if path.is_file())
    scans = run_with_threads(
        xml_files, _read_authority_pids, workers=workers, desc="Reading publications"
    )
    summary = PersonMigrationSummary(xml_files=len(xml_files))
    authority_pids: set[str] = set()
    for xml_path, pids, error in scans:
        authority_pids.update(pids)
        if error is not None:
            summary.scan_errors[str(xml_path)] = error
    summary.unique_persons = len(authority_pids)
    if not authority_pids:
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
        logger.error("Failed to initialize Cora context: %s", error)
        summary.initialization_error = str(error)
        return summary
    summary.outcomes = run_with_threads(
        sorted(authority_pids),
        partial(_migrate_person, context=context),
        workers=workers,
        desc="Migrating persons",
        status_order=[
            ("CREATED", "\u2705"),
            ("SKIPPED", "\u27a1\ufe0f"),
            ("FAILED", "\u274c"),
        ],
    )
    return summary
