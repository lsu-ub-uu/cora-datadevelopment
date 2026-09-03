import logging

from common.xml_utils import create_text, pretty_print_xml, create_group
from common.logging_config import configure_logging
from cora.context import CoraContext
from cora.list_records import list_records
from common.arg_parser import create_argument_parser, common_arguments
from cora.update import update_record

logger = logging.getLogger(__name__)


def main():
    """
    Updates subject elements with authority 'diva' in diva-output records according to change model.

    Removes the original subject element and creates new subject elements
    for each topic under the original subject.
    """
    args = _parse_args()
    configure_logging()

    logger.info("==== Begin updating diva-output subject authority model ====")
    logger.info(f"==== system={args.system} ====")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )
    output_records = list_records(context, "diva-output")
    logger.info(f"Number of diva-output records: {len(output_records)}")

    updated = 0
    failed = 0
    skipped = 0

    for record in output_records:
        record_id = record.findtext("./data/output/recordInfo/id")
        output = record.find("./data/output")
        assert output is not None, "Output element not found in record"

        subject = output.find("./subject[@authority='diva']")
        if subject is None:
            skipped += 1
            logger.info(f"Skipped record {record_id}: no subject with authority diva")
            continue
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
        if result.success:
            updated += 1
            logger.info(f"Record {record_id} updated successfully")
        else:
            failed += 1
            logger.error(f"Failed to update record {record_id}: {result.error}")

    _log_summary(logger, len(output_records), updated, failed, skipped)


def _log_summary(logger, total: int, updated: int, failed: int, skipped: int):
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
