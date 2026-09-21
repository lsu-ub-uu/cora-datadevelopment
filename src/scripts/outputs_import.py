import os
import sys
import time
from collections.abc import Callable
from xml.etree import ElementTree as ET
from common.arg_parser import (
    create_argument_parser,
    classic_arguments,
    cora_url_argument,
)
from common.logging_config import configure_logging
from cora.context import CoraContext
from fedora_to_cora.output_migrate import output_migrate
from fedora_to_cora.output_migration_result import OutputMigrationResult
from fedora_to_cora.output_relations_migrate import migrate_output_relations
from common.common_data import read_source_xml
from common.print_logo import print_logo
from multiprocessing import Pool
from tqdm import tqdm
from scripts.util.outputs_import_report.save_reports import save_reports

context = None


def main():
    """Main entry point for the outputs import script."""

    print_logo()

    configure_logging()
    args = _parse_args()
    outputs_import(
        xml_dir=args.xml_dir,
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        processes=args.processes,
        apply=args.apply,
        limit=args.limit,
        binaries=args.binaries,
        pids=args.pids.split(",") if args.pids else None,
        fedora_url=args.fedora_url or "",
        cora_url=args.cora_url,
    )


def outputs_import(
    xml_dir: str,
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
    apply: bool,
    limit: int | None = None,
    binaries: bool = False,
    pids: list[str] | None = None,
    fedora_url: str = "",
    cora_url: str | None = None,
):
    start_time = time.perf_counter()

    source_record_paths = _read_source_record_paths(xml_dir, limit)

    if pids is not None:
        source_record_paths = _filter_source_record_paths_by_pids(
            source_record_paths, pids
        )

    print(
        f"Starting migration of {len(source_record_paths)} records to {system} system..."
    )

    migration_results = _migrate_outputs(
        source_record_paths=source_record_paths,
        system=system,
        login_id=login_id,
        app_token=app_token,
        processes=processes,
        apply=apply,
        binaries=binaries,
        fedora_url=fedora_url,
        cora_url=cora_url,
    )

    relation_migration_results = _migrate_output_relations(
        migration_results=migration_results,
        system=system,
        login_id=login_id,
        app_token=app_token,
        processes=processes,
        cora_url=cora_url,
    )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Migration completed in {elapsed_time:.2f} seconds.")

    print(
        f"Successfully migrated {len([r for r in migration_results if r.status == 'SUCCESS'])} records."
    )

    save_reports(
        migration_results,
        xml_dir=xml_dir,
        system=system,
        apply=apply,
        binaries=binaries,
        cora_url=cora_url,
        output_dir="reports",
        relation_results=relation_migration_results,
    )


def _migrate_outputs(
    source_record_paths: list[str],
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
    apply: bool,
    binaries: bool = False,
    fedora_url: str = "",
    cora_url: str | None = None,
):
    counts = {
        "SUCCESS": 0,
        "CLASSIC_QUALITY": 0,
        "FAILED": 0,
        "SKIPPED": 0,
        "INPUT_VALIDATION_FAILED": 0,
    }
    return _run_pool_with_progress(
        work_items=source_record_paths,
        worker=_migrate_record,
        processes=processes,
        initargs=(
            system,
            login_id,
            app_token,
            cora_url,
            apply,
            binaries,
            fedora_url,
        ),
        progress_desc="Importing records",
        counts=counts,
        status_order=[
            ("SUCCESS", "✅"),
            ("CLASSIC_QUALITY", "⚠️"),
            ("FAILED", "❌"),
            ("SKIPPED", "➡️"),
            ("INPUT_VALIDATION_FAILED", "⛔"),
        ],
    )


def _migrate_output_relations(
    migration_results: list[OutputMigrationResult],
    processes: int,
    system: str,
    login_id: str,
    app_token: str,
    cora_url: str | None = None,
):
    counts = {
        "UPDATED": 0,
        "NO_RELATIONS": 0,
        "FAILED": 0,
    }
    return _run_pool_with_progress(
        work_items=migration_results,
        worker=_update_relations_for_output,
        processes=processes,
        initargs=(system, login_id, app_token, cora_url),
        progress_desc="Importing output relations",
        counts=counts,
        status_order=[
            ("UPDATED", "✅"),
            ("NO_RELATIONS", "➡️"),
            ("FAILED", "❌"),
        ],
    )


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            "--xml-dir": {
                "help": "Directory containing XML files to process",
                "required": True,
            },
            **cora_url_argument,
            **classic_arguments,
            "--system": {
                "default": "pre",
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--processes": {
                "type": int,
                "default": 2,
                "help": "Number of processes",
            },
            "--apply": {
                "action": "store_true",
                "help": "Create records in Cora. (If not set, will behave as a dry-run)",
            },
            "--limit": {
                "type": int,
                "help": "Limit the number of processed files (for testing purposes)",
                "default": None,
            },
            "--binaries": {
                "action": "store_true",
                "help": "Also migrate binaries associated with the publications",
                "default": False,
            },
            "--pids": {
                "help": "Comma-separated list of PIDs to process (for testing purposes)",
            },
        },
    )

    return parser.parse_args()


def _init_context(
    system,
    login_id,
    app_token,
    cora_url,
    apply_flag=False,
    binaries_flag=False,
    fedora_url_arg="",
):
    global context, apply, with_binaries, fedora_url
    configure_logging()
    context = CoraContext(
        system=system,
        login_id=login_id,
        app_token=app_token,
        cora_url=cora_url,
    )
    apply = apply_flag
    with_binaries = binaries_flag
    fedora_url = fedora_url_arg


def _run_pool_with_progress(
    work_items: list,
    worker: Callable,
    processes: int,
    initargs: tuple,
    progress_desc: str,
    counts: dict[str, int],
    status_order: list[tuple[str, str]],
):
    results = []

    with Pool(
        processes,
        _init_context,
        initargs=initargs,
    ) as pool, tqdm(total=len(work_items), desc=progress_desc) as progress:
        for result in pool.imap_unordered(worker, work_items):
            counts[result.status] += 1
            results.append(result)
            progress.set_postfix_str(_format_progress_counts(counts, status_order))
            progress.update(1)
    return results


def _format_progress_counts(
    counts: dict[str, int], status_order: list[tuple[str, str]]
) -> str:
    return " | ".join(f"{icon} {counts[status]}" for status, icon in status_order)


def _migrate_record(source_record_path: str):
    assert context is not None, "Context must be initialized before migrating records"
    source_record = read_source_xml(source_record_path)
    return output_migrate(
        source_record,
        context,
        apply,
        with_binaries=with_binaries,
        fedora_url=fedora_url,
    )


def _update_relations_for_output(migration_result: OutputMigrationResult):
    assert context is not None, "Context must be initialized"

    return migrate_output_relations(migration_result, context)


def _read_source_record_paths(xml_dir: str, limit: int | None = None) -> list[str]:
    source_record_paths = [
        os.path.join(xml_dir, filename)
        for filename in os.listdir(xml_dir)
        if filename.endswith(".xml")
    ]

    if limit is not None:
        return source_record_paths[:limit]

    return source_record_paths


def _filter_source_record_paths_by_pids(
    source_record_paths: list[str], pids: list[str]
) -> list[str]:
    pid_set = set(pids)
    filtered_paths = []

    for source_record_path in source_record_paths:
        source_record = read_source_xml(source_record_path)
        if source_record.findtext("pid") in pid_set:
            filtered_paths.append(source_record_path)

    return filtered_paths


if __name__ == "__main__":
    main()
