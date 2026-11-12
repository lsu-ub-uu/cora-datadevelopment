import logging
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from common.xml_utils import create_text
from common.logging_config import configure_logging
from common.environment import load_environment
from cora_python_client import CoraClient, CoraRecord
from cora.list_records import list_records
from common.arg_parser import create_argument_parser, common_arguments
from cora.update import update_record

logger = logging.getLogger(__name__)


def main():
    """
    Updates binary records by setting their status to "done" if not already set.
    """
    args = _parse_args()
    configure_logging()

    logger.info("==== Begin updating binary records ====")

    cora_client = CoraClient(args.cora_url)
    cora_client.login_with_app_token(login_id=args.login_id, app_token=args.app_token)

    logger.info(f"==== system={args.system} ====")

    fix_records(cora_client, args.workers)


def fix_records(cora_client: CoraClient, workers: int):
    binary_record_list = cora_client.list_records(record_type="binary")
    logger.info(f"Number of binary records: {len(binary_record_list.records)}")

    results = run_with_threads(
        binary_record_list.records,
        lambda record: fix_record(record, cora_client),
        workers,
        "Updating binary records",
    )

    _log_summary(
        len(binary_record_list.records),
        updated=results.count("updated"),
        failed=results.count("failed"),
        skipped=results.count("skipped"),
    )


def fix_record(record: CoraRecord, cora_client: CoraClient):
    record_info = record.data_group.find("./recordInfo")
    assert record_info is not None, "Binary recordInfo element not found"

    status = record_info.find("./status")
    if status is None:
        status = create_text("status", value="done")
        assert status is not None
        record_info.append(status)
    else:
        return "skipped"
    try:
        cora_client.update_record(record)
        return "updated"
    except Exception as e:
        logger.error(f"Failed to update record {record.id}: {e}")
        return "failed"


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
