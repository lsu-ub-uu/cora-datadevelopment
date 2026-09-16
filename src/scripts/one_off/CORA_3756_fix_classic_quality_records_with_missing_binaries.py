import logging
from common.common_data import read_source_xml
from common.logging_config import configure_logging
from common.arg_parser import (
    create_argument_parser,
    common_arguments,
    classic_arguments,
)
from common.xml_utils import pretty_print_xml
from cora.context import Context, CoraContext
from fedora_to_cora.attachments_migrate import attachments_migrate
from cora.get_record import get_record

record_ids = ["267", "1976", "1563", "32", "919", "304", "183"]

logger = logging.getLogger(__name__)


def main():
    configure_logging()
    args = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={**common_arguments, **classic_arguments},
    ).parse_args()

    logger.info(
        "==== Beginning processing of classic quality records with missing binaries ===="
    )
    logger.info(f"Record IDs to process: {record_ids}")

    context = CoraContext(
        args.system,
        args.login_id,
        args.app_token,
        cora_url=args.cora_url,
    )

    _fix_records(
        context,
        fedora_url=args.fedora_url,
        xml_path=args.xml_path,
    )


def _fix_records(context: Context, fedora_url: str, xml_path: str):
    for record_id in record_ids:
        logger.info(f"Processing record ID: {record_id}")

        cora_record = get_record(context, "diva-output", record_id)

        pid = cora_record.findtext("./data/output/recordInfo/oldId")
        assert pid is not None, f"PID for record with ID {record_id} not found"

        source_record = read_source_xml(f"{xml_path}/{pid}.xml")

        attachments_migrate(source_record, cora_record, context, fedora_url=fedora_url)

        logger.info(f"Finished processing record ID: {record_id}")


if __name__ == "__main__":
    main()
