from pathlib import Path
import sys

from common.arg_parser import common_arguments, create_argument_parser
from common.environment import load_environment
from common.logging_config import configure_logging
from cora.context import resolve_cora_workers
from fedora_to_cora.persons_migrate import migrate_persons


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
    summary = migrate_persons(
        args.xml_dir,
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=workers,
        cora_url=args.cora_url,
    )
    print(
        f"XML files: {summary.xml_files} | Read: {summary.files_read}"
        f" | Failed: {len(summary.scan_errors)}"
    )
    print(f"Unique persons: {summary.unique_persons}")
    if summary.initialization_error is not None:
        print(
            f"Failed to initialize Cora context: {summary.initialization_error}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    counts = summary.counts
    print(
        f"Created: {counts['CREATED']} | Skipped: {counts['SKIPPED']}"
        f" | Failed: {counts['FAILED']}"
    )
    if counts["FAILED"]:
        print("Migration errors:")
        for error_message, authority_pids_for_error in summary.errors.items():
            pids = ", ".join(authority_pids_for_error)
            print(
                f"  {len(authority_pids_for_error)}x {error_message}"
                f" | authorityPid(s): {pids}"
            )
    if summary.has_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
