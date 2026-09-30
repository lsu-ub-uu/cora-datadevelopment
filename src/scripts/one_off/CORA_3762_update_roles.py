import logging
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from common.xml_utils import create_text, pretty_print_xml, create_group
from common.logging_config import configure_logging
from cora.context import Context, CoraContext
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
    if not args.apply:
        logger.info("Running in dry-run mode (no changes will be applied)")

    context = CoraContext(
        args.system, args.login_id, args.app_token, cora_url=args.cora_url
    )

    fix_records(context, apply=args.apply)


def fix_records(context: Context, apply: bool):
    output_records = list_records(context, "diva-output")
    logger.info(f"Number of diva-output records: {len(output_records)}")

    role_terms_with_repeat_id = 0
    person_role_terms_with_repeat_id = 0
    for record in output_records:
        person_role_term_with_repeat_id = record.findall(
            "./data/output/name[@type='personal']/role/roleTerm[@repeatId]"
        )
        role_term_with_repeat_id = record.findall(".//name/role/roleTerm[@repeatId]")
        role_terms_with_repeat_id += len(role_term_with_repeat_id)
        person_role_terms_with_repeat_id += len(person_role_term_with_repeat_id)

    print(f"Number of role terms with repeatId: {role_terms_with_repeat_id}")
    print(
        f"Number of person role terms with repeatId: {person_role_terms_with_repeat_id}"
    )

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


def fix_record(record: ET.Element, context: Context, apply: bool):
    record_id = record.findtext("./data/output/recordInfo/id")
    output = record.find("./data/output")
    assert output is not None, "Output element not found in record"

    persons = record.findall("./data/output/name[@type='personal']")

    if not persons:
        logger.info(f"Skipped record {record_id}: no personal name found")
        return "skipped"

    role_terms_with_repeat_id = output.findall(
        "./name[@type='personal']/role/roleTerm[@repeatId]"
    )
    if len(role_terms_with_repeat_id) == 0:
        logger.info(f"Skipped record without role terms to migrate {record_id}")
        return "skipped"

    record_changed = False

    for person in persons:
        roles = person.findall("./role")
        if len(roles) == 0:
            logger.info(f"Skipped person without rolesin record {record_id}")
            continue

        role_terms_with_repeat_id = person.findall("./role/roleTerm[@repeatId]")
        if len(role_terms_with_repeat_id) == 0:
            logger.info(
                f"Skipped person without role terms to migrate in record {record_id}"
            )
            continue

        if len(roles) > 1:
            logger.info(f"Skipped person with multiple roles in record {record_id}")
            continue

        role = roles[0]

        role_terms = person.findall("./role/roleTerm")

        person.remove(role)

        for role_term in role_terms:
            new_role = create_group(
                "role",
                repeatId=role_term.attrib.get("repeatId"),
                children=[
                    create_group(
                        "roleTerm",
                        children=[
                            create_text("roleTerm", role_term.text),
                        ],
                    )
                ],
            )
            assert new_role is not None, "Failed to create new role element"
            person.append(new_role)
            record_changed = True

    if record_changed:
        logger.debug(f"Transformed record {record_id}: {pretty_print_xml(record)}")
        if apply:
            result = update_record(record, context)
            return "updated" if result.success else "failed"
        else:
            return "updated"
    else:
        logger.info(f"No changes made to record {record_id}")
        return "skipped"


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


def _parse_args():
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments=common_arguments,
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
