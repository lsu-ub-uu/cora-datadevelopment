import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from common.common_data import create_record_link, read_source_xml
from common.environment import load_environment
from common.logging_config import configure_logging
from common.arg_parser import create_argument_parser, common_arguments
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml
from cora.context import Context, CoraContext
from cora.list_records import list_records
from cora.update import update_record
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from fedora_to_cora.migrate_old_record import (
    old_record_migrate,
)

logger = logging.getLogger(__name__)


def main():
    """Update existing in prod environment output with oldRecord."""
    load_environment()
    args = _parse_args()
    configure_logging()
    logger.info("==== Begin updating diva-output with oldRecord recordLink ====")
    if not args.apply:
        logger.info("Running in dry-run mode (no changes will be applied)")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )
    logger.info(f"==== system={context.get_system()} ====")

    fix_records(context, apply=args.apply, xml_dir=args.xml_dir)


def fix_records(context: Context, apply: bool, xml_dir: str):
    output_records = list_records(context, "diva-output")
    logger.info(f"Number of diva-output records: {len(output_records)}")

    results = run_with_threads(
        output_records,
        lambda record: fix_record(record, context, apply, xml_dir),
        context.get_workers(),
        "Updating diva-output records",
    )
    _log_summary(
        len(output_records),
        updated=results.count("updated"),
        failed=results.count("failed"),
        skipped=results.count("skipped"),
        apply=apply,
    )


def fix_record(record: ET.Element, context: Context, apply: bool, xml_dir: str) -> str:
    output = record.find("./data/output")
    assert output is not None, "output should not be None"

    old_id = output.findtext("./recordInfo/oldId")
    if old_id is None:
        logger.info(
            f"old_id is missing in the output record with id {record.findtext('./data/output/recordInfo/id')}"
        )
        return "skipped"

    try:
        old_record_xml = _get_old_record_xml(old_id, xml_dir)
    except FileNotFoundError:
        logger.warning(
            f"Skipping output {old_id}: old record XML not found at {Path(xml_dir) / f'{old_id}.xml'}"
        )
        return "skipped"

    if not apply:
        logger.info(
            f"Dry-run mode: would create an old record and link it to output {old_id}"
        )
        return "updated"

    migration_result = old_record_migrate(old_record_xml, context)
    if migration_result.status == "FAILED":
        logger.error(
            f"Failed to create old record for {old_id}: {migration_result.error}"
        )
        return "failed"
    record_id = migration_result.cora_old_record_id
    if migration_result.status == "SKIPPED":
        record_id = get_cora_id_by_old_id(
            old_id, record_type="diva-oldRecord", context=context
        )
    assert record_id is not None, "Created old record should have an ID"

    update_record_info_with_old_record_link(record_id, output)
    result = update_record(record, context)
    if not result.success:
        logger.error(
            f"Failed to update record {old_id} with data\n\n: {pretty_print_xml(record)}"
        )
        return "failed"

    logger.info(f"Updated output {old_id} with old record {record_id}")
    return "updated"


def _log_summary(total: int, updated: int, failed: int, skipped: int, apply: bool):
    logger.info("==================== Summary ====================")
    logger.info(f"Total diva-output records: {total}")
    logger.info(
        f"Not updated (dry-run mode): {updated}" if not apply else f"Updated: {updated}"
    )
    logger.info(f"Failed: {failed}")
    logger.info(f"Skipped: {skipped}")
    logger.info("================================================")

    print("==================== Summary ====================")
    print(f"Total diva-output records: {total}")
    print(
        f"Not updated (dry-run mode): {updated}" if not apply else f"Updated: {updated}"
    )
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("================================================")


def update_record_info_with_old_record_link(
    cora_old_record_id: str, output: ET.Element
):
    assert output is not None, "record should not be None"
    assert cora_old_record_id is not None, "pid should not be None"

    record_info = output.find("./recordInfo")
    assert record_info is not None, "recordInfo should not be None"
    old_record_tag = create_record_link(
        "oldRecord", "diva-oldRecord", cora_old_record_id
    )
    assert old_record_tag is not None, "old_record_tag should not be None"
    record_info.append(old_record_tag)


def _get_old_record_xml(old_id: str, xml_dir: str) -> ET.Element:
    old_record_path = Path(xml_dir) / f"{old_id}.xml"
    return read_source_xml(old_record_path)


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            "--xml-dir": {
                "help": "Directory containing XML files to process",
                "required": True,
            },
            **common_arguments,
        },
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
