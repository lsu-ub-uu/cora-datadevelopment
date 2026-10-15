import logging
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from common.xml_utils import create_text
from common.logging_config import configure_logging
from common.environment import load_environment
from cora.context import Context, CoraContext
from cora.list_records import list_records
from common.arg_parser import create_argument_parser, common_arguments
from cora.update import update_record

logger = logging.getLogger(__name__)


def main():
    """
    Updates binary records by setting their status to "done" if not already set.
    """
    load_environment()
    args = _parse_args()
    configure_logging()

    logger.info("==== Begin updating binary records ====")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )
    logger.info(f"==== system={context.get_system()} ====")

    fix_records(context)


def fix_records(context: Context):
    binary_records = list_records(context, "binary")
    logger.info(f"Number of binary records: {len(binary_records)}")

    results = run_with_threads(
        binary_records,
        lambda record: fix_record(record, context),
        context.get_workers(),
        "Updating binary records",
    )

    _log_summary(
        len(binary_records),
        updated=results.count("updated"),
        failed=results.count("failed"),
        skipped=results.count("skipped"),
    )


def fix_record(record: ET.Element, context: Context):
    record_info = record.find("./data/binary/recordInfo")
    assert record_info is not None, "Binary recordInfo element not found"

    status = record_info.find("./status")
    if status is None:
        status = create_text("status", value="done")
        assert status is not None
        record_info.append(status)
    else:
        return "skipped"

    result = update_record(record, context)
    return "updated" if result.success else "failed"


def _log_summary(total: int, updated: int, failed: int, skipped: int):
    logger.info("==================== Summary ====================")
    logger.info(f"Total binary records: {total}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Skipped: {skipped}")
    logger.info("================================================")

    print("==================== Summary ====================")
    print(f"Total binary records: {total}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("================================================")


def _parse_args():
    parser = create_argument_parser(
        description="Updates binary records by setting their status to 'done' if not already set.",
        arguments={
            key: value for key, value in common_arguments.items() if key != "--apply"
        },
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
