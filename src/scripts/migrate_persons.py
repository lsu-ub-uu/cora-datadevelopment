import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import partial
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from common.arg_parser import common_arguments, create_argument_parser
from common.common_data import read_source_xml
from common.environment import load_environment
from common.logging_config import configure_logging
from common.threads import run_with_threads
from cora.context import Context, CoraContext, resolve_cora_workers
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


def _read_authority_pids(xml_path: Path) -> tuple[set[str], bool]:
    try:
        publication = read_source_xml(xml_path)
    except (ET.ParseError, OSError) as error:
        logger.error("Failed to read %s: %s", xml_path, error)
        return set(), False
    authority_pids = {
        element.text.strip()
        for element in publication.findall(".//authorityPid")
        if element.text and element.text.strip()
    }
    return authority_pids, True


def _migrate_person(authority_pid: str, context: Context) -> PersonMigrationOutcome:
    try:
        result = migrate_person(authority_pid, context)
    except Exception as error:
        result = MigratePersonResult("FAILED", None, str(error))
    if result.status == "FAILED":
        logger.error("Failed to migrate %s: %s", authority_pid, result.error)
    return PersonMigrationOutcome(authority_pid, result)


def main() -> None:
    load_environment()
    parser = create_argument_parser(
        description="Migrate persons referenced in Fedora publication XML files to Cora",
        arguments={
            "--xml-dir": {
                "help": "Directory containing publication XML files",
                "type": Path,
                "required": True,
            },
            **{
                name: common_arguments[name]
                for name in (
                    "--workers",
                    "--system",
                    "--login-id",
                    "--app-token",
                    "--cora-url",
                )
            },
        },
    )
    args = parser.parse_args()
    if not args.xml_dir.is_dir():
        parser.error(f"Not a directory: {args.xml_dir}")
    try:
        workers = resolve_cora_workers(args.workers)
    except ValueError:
        parser.error("Workers must be a positive integer")
    if workers < 1:
        parser.error("Workers must be a positive integer")

    configure_logging()
    xml_files = sorted(path for path in args.xml_dir.glob("*.xml") if path.is_file())
    scans = run_with_threads(
        xml_files, _read_authority_pids, workers=workers, desc="Reading publications"
    )
    authority_pids: set[str] = set()
    for pids, _ in scans:
        authority_pids.update(pids)
    failed_files = sum(not success for _, success in scans)
    print(
        f"XML files: {len(xml_files)} | Read: {len(xml_files) - failed_files}"
        f" | Failed: {failed_files}"
    )
    print(f"Unique persons: {len(authority_pids)}")

    results: list[PersonMigrationOutcome] = []
    if authority_pids:
        try:
            context = CoraContext(
                system=args.system,
                login_id=args.login_id,
                app_token=args.app_token,
                workers=workers,
                cora_url=args.cora_url,
            )
        except Exception as error:
            logger.error("Failed to initialize Cora context: %s", error)
            print(f"Failed to initialize Cora context: {error}", file=sys.stderr)
            raise SystemExit(1) from error
        results = run_with_threads(
            sorted(authority_pids),
            partial(_migrate_person, context=context),
            workers=workers,
            desc="Migrating persons",
            status_order=[
                ("CREATED", "✅"),
                ("SKIPPED", "➡️"),
                ("FAILED", "❌"),
            ],
        )
    counts = Counter(result.status for result in results)
    print(
        f"Created: {counts['CREATED']} | Skipped: {counts['SKIPPED']}"
        f" | Failed: {counts['FAILED']}"
    )
    if counts["FAILED"]:
        error_pids: dict[str, list[str]] = defaultdict(list)
        for result in results:
            if result.status == "FAILED":
                error_pids[result.error or "Unknown error"].append(result.authority_pid)
        print("Migration errors:")
        for error_message, authority_pids_for_error in sorted(
            error_pids.items(), key=lambda item: (-len(item[1]), item[0])
        ):
            pids = ", ".join(sorted(authority_pids_for_error))
            print(
                f"  {len(authority_pids_for_error)}x {error_message}"
                f" | authorityPid(s): {pids}"
            )
    if failed_files or counts["FAILED"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
