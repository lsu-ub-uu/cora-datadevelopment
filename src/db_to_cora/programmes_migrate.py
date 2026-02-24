import xml.etree.ElementTree as ET
from classic.get_programmes import get_programmes
from cora.create import create_record, is_success_result
from multiprocessing import Pool
from cora.context import CoraContext
from tqdm import tqdm
from typing import Literal
from db_to_cora.subject_programme_course_transform import transform_programme
from db_to_cora.update_relations import RelationMapping, update_relations

context = None


def _init_context(system: str, login_id: str, app_token: str):
    global context
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)


def _migrate_programme(
    source_record: ET.Element,
) -> tuple[
    Literal["SUCCESS", "FAILED", "SKIPPED"], tuple[ET.Element, ET.Element] | None
]:
    assert context is not None, "Context must be initialized before migrating records"
    transformed_programme = transform_programme(source_record)
    result = create_record(
        transformed_programme, record_type="diva-programme", context=context
    )
    if is_success_result(result):
        record_mapping = (source_record, result.response_data)
        return ("SUCCESS", record_mapping)
    else:
        old_id = source_record.findtext("./old_id")
        if result.error and (
            f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
            in result.error
        ):
            context.log(
                f"Record with old id {old_id} already exists. Skipping creation.",
                level="warning",
            )
            return ("SKIPPED", None)
        context.log(f"Failed to create record: {result.error}", level="error")
        return ("FAILED", None)


def migrate_programmes(
    domain: str,
    db_user: str,
    db_password: str,
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
):
    counts = {"SUCCESS": 0, "FAILED": 0, "SKIPPED": 0}

    classic_programmes = get_programmes(
        domain=domain, db_user=db_user, db_password=db_password
    ).findall(".//DATA_RECORD")

    record_mappings = []
    with (
        Pool(
            processes=min(len(classic_programmes), processes),
            initializer=_init_context,
            initargs=(
                system,
                login_id,
                app_token,
            ),
        ) as pool,
        tqdm(total=len(classic_programmes), desc="Importing records") as progress,
    ):
        for status, record_mapping in pool.imap_unordered(
            _migrate_programme, classic_programmes
        ):
            counts[status] += 1
            if record_mapping is not None:
                record_mappings.append(record_mapping)
            progress.set_postfix_str(
                f"✅ {counts['SUCCESS']} | ❌ {counts['FAILED']} | ➡️ {counts['SKIPPED']}"
            )
            progress.update(1)

    update_relations(
        record_mappings,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="broader_id",
                new_relation_link="programme",
                new_relation_type="broader",
            ),
            RelationMapping(
                old_relation_tag="earlier_id",
                new_relation_link="programme",
                new_relation_type="earlier",
            ),
        ],
        record_type="diva-programme",
        context=CoraContext(system=system, login_id=login_id, app_token=app_token),
    )
