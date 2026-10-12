import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from common.environment import load_environment
from common.logging_config import configure_logging
from common.arg_parser import create_argument_parser, common_arguments
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml
from cora.context import Context, CoraContext
from cora.list_records import list_records
from cora.update import update_record
from fedora_to_cora.migrate_old_record import old_record_migrate, update_record_info

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

    fix_records(context, apply=args.apply)


def fix_records(context: Context, apply: bool):
    output_records = list_records(context, "diva-output")
    logger.info(f"Number of diva-output records: {len(output_records)}")

    results = run_with_threads(
        output_records,
        lambda record: fix_record(record, context, apply),
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


def fix_record(record: ET.Element, context: Context, apply: bool) -> str:
    old_id = record.findtext(".//oldId")
    assert old_id is not None, "old_id should not be None"
    old_record = _get_old_record(old_id)

    if not apply:
        logger.info(
            f"Dry-run mode: would create an old record and link it to output {old_id}"
        )
        print(old_id)
        return "updated"

    success, error, record_id = old_record_migrate(old_record, context)
    if not success or record_id is None:
        logger.error(f"Failed to create old record for {old_id}: {error}")
        return "failed"

    output = update_record_info(record_id, record)
    result = update_record(output, context)
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


def _get_old_record(old_id: str) -> ET.Element:
    old_record_path = Path("data/fedora_xml/nordiskamuseet") / f"{old_id}.xml"
    return ET.parse(old_record_path).getroot()


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments=common_arguments,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
