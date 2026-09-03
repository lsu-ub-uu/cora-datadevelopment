from logging import Logger
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from common.xml_utils import create_text, pretty_print_xml, create_group
from common.run_rotating_logger import RunRotatingLogger
from cora.context import Context, CoraContext
from cora.list_records import list_records
from common.arg_parser import create_argument_parser, common_arguments
from cora.update import update_record


def main():
    """
    Updates subject elements with authority 'diva' in diva-output records according to change model.

    Removes the original subject element and creates new subject elements
    for each topic under the original subject.
    """
    args = _parse_args()
    logger = RunRotatingLogger(
        "data", "logs/CORA-3700_update_subject_authority_diva_model.log"
    ).get()

    logger.info("==== Begin updating diva-output subject authority model ====")
    logger.info(f"==== system={args.system} ====")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )

    fix_records(logger, context)


def fix_records(logger: Logger, context: Context):
    output_records = list_records(context, "diva-output")
    logger.info(f"Number of diva-output records: {len(output_records)}")

    results = run_with_threads(
        output_records,
        lambda record: _fix_record(record, context, logger),
        context.get_workers(),
        "Updating diva-output records",
    )

    _log_summary(
        logger,
        len(output_records),
        updated=results.count("updated"),
        failed=results.count("failed"),
        skipped=results.count("skipped"),
    )


def _fix_record(record: ET.Element, context: Context, logger: Logger):
    record_id = record.findtext("./data/output/recordInfo/id")
    output = record.find("./data/output")
    assert output is not None, "Output element not found in record"

    subject = output.find("./subject[@authority='diva']")
    if subject is None:
        logger.info(f"Skipped record {record_id}: no subject with authority diva")
        return "skipped"
    topics = output.findall("./subject[@authority='diva']/topic")

    output.remove(subject)

    for i, topic in enumerate(topics):
        linked_record_id = topic.findtext("./linkedRecordId")
        new_subject = create_group(
            "subject",
            authority="diva",
            repeatId=str(i),
            children=[
                create_group(
                    "topic",
                    children=[
                        create_text("linkedRecordType", "diva-subject"),
                        create_text("linkedRecordId", linked_record_id),
                    ],
                )
            ],
        )
        assert new_subject is not None, "Failed to create new subject element"
        output.append(new_subject)

    logger.debug(f"Transformed record {record_id}: {pretty_print_xml(record)}")
    result = update_record(record, context)
    return "updated" if result.success else "failed"


def _log_summary(logger: Logger, total: int, updated: int, failed: int, skipped: int):
    logger.info("==================== Summary ====================")
    logger.info(f"Total diva-output records: {total}")
    logger.info(f"Updated: {updated}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Skipped (no diva subject): {skipped}")
    logger.info("================================================")


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments=common_arguments,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
