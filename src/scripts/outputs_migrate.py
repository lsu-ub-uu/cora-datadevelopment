import xml.etree.ElementTree as ET
import logging
from common.arg_parser import (
    create_argument_parser,
    classic_arguments,
    cora_url_argument,
)
from classic.get_classic_publications import get_classic_publications
from fedora_to_cora.output_migrate import output_migrate, OutputMigrationResult
from common.logging_config import configure_logging
from cora.context import CoraContext
from tqdm import tqdm

logger = logging.getLogger(__name__)


def main():
    args = _parse_args()

    configure_logging()
    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
        cora_url=args.cora_url,
    )

    pids = args.pids.split(",")
    results: list[OutputMigrationResult] = []
    progress = tqdm(total=len(pids), desc="Migrating outputs")

    def on_success(pid: str, record: ET.Element):
        result = output_migrate(
            record,
            context,
            apply=args.apply,
            with_binaries=args.binaries,
            fedora_url=args.fedora_url,
        )
        results.append(result)
        progress.update(1)
        logger.info(f"{pid}: {result.status}")

    def on_error(error: str):
        logger.error(error)
        progress.update(1)

    get_classic_publications(
        pids,
        workers=args.workers,
        on_success=on_success,
        on_error=on_error,
        fedora_url=args.fedora_url,
    )

    progress.close()
    _print_summary(results)


def _parse_args():
    parser = create_argument_parser(
        description="Fetch publications from Classic Fedora and migrate them to Cora",
        arguments={
            "--pids": {
                "required": True,
                "help": "Comma-separated list of publication PIDs to migrate",
            },
            **cora_url_argument,
            **classic_arguments,
            "--system": {
                "default": "pre",
                "help": "Target Cora system",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--workers": {
                "type": int,
                "default": 16,
                "help": "Number of worker threads",
            },
            "--apply": {
                "action": "store_true",
                "help": "Create records in Cora (dry-run if not set)",
            },
            "--binaries": {
                "action": "store_true",
                "help": "Also migrate binaries",
                "default": False,
            },
        },
    )
    return parser.parse_args()


def _print_summary(results: list[OutputMigrationResult]):
    counts = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1

    print("\n=== Migration Summary ===")
    print(f"Total: {len(results)}")
    for status, count in counts.items():
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
