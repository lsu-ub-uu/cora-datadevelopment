import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from common.common_data import create_record_link, read_source_xml
from common.environment import load_environment
from common.logging_config import configure_logging
from common.arg_parser import create_argument_parser, common_arguments
from common.threads import run_with_threads
from common.xml_utils import pretty_print_xml
from cora.get_record import get_record
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
    logger.info("==== Begin updating diva-oldRecord with oldRecord recordLink ====")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )
    logger.info(f"==== system={context.get_system()} ====")

    fix_records(context)


def fix_records(context: Context):
    old_records = list_records(context, "diva-oldRecord")
    logger.info(f"Number of diva-oldRecord records: {len(old_records)}")

    results = run_with_threads(
        old_records,
        lambda record: fix_record(record, context),
        context.get_workers(),
        "Updating diva-oldRecord records",
    )
    _log_summary(
        len(old_records),
        updated=results.count("updated"),
        failed=results.count("failed"),
        skipped=results.count("skipped"),
    )


def fix_record(record: ET.Element, context: Context) -> str:

    binary_record_id = record.findtext("./data/oldRecord/record/linkedRecordId")
    if not binary_record_id:
        logger.warning("Skipping record: linkedRecordId is missing")
        return "skipped"

    try:
        binary = get_record(context, "binary", binary_record_id)
    except Exception as e:
        logger.error(f"Failed to get binary record: {e}")
        return "failed"

    visibility = binary.find("./data/binary/recordInfo/visibility")
    assert visibility is not None, "visibility should not be None"
    visibility.text = "unpublished"

    result = update_record(binary, context)
    if not result.success:
        logger.error("Failed to update binary record")
        return "failed"

    return "updated"


def _log_summary(total: int, updated: int, failed: int, skipped: int):
    logger.info("==================== Summary ====================")
    logger.info(f"Total diva-oldRecord records: {total}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Skipped: {skipped}")
    logger.info("================================================")

    print("==================== Summary ====================")
    print(f"Total diva-oldRecord records: {total}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("================================================")


def _parse_args():
    parser = create_argument_parser(
        description="Update old record binaries to unpublished",
        arguments=common_arguments,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
