import xml.etree.ElementTree as ET
from classic.get_funders import get_funders
from db_to_cora.funder_transform import transform_funder
from cora.create import create_record, is_success_result
from multiprocessing import Pool
from cora.context import CoraContext
from tqdm import tqdm
from typing import Literal

context = None


def _init_context(system: str, login_id: str, app_token: str):
    global context
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)


def _migrate_funder(
    source_record: ET.Element,
) -> Literal["SUCCESS", "FAILED", "SKIPPED"]:
    assert context is not None, "Context must be initialized before migrating records"
    transformed_funder = transform_funder(source_record)
    result = create_record(
        transformed_funder, record_type="diva-funder", context=context
    )
    if is_success_result(result):
        return "SUCCESS"
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
            return "SKIPPED"
        context.log(f"Failed to create record: {result.error}", level="error")
        return "FAILED"


def migrate_funders(
    db_user: str,
    db_password: str,
    system: str,
    login_id: str,
    app_token: str,
    processes: int,
):
    counts = {"SUCCESS": 0, "FAILED": 0, "SKIPPED": 0}

    classic_funders = get_funders(db_user=db_user, db_password=db_password).findall(
        ".//DATA_RECORD"
    )
    with (
        Pool(
            processes=processes,
            initializer=_init_context,
            initargs=(
                system,
                login_id,
                app_token,
            ),
        ) as pool,
        tqdm(total=len(classic_funders), desc="Importing records") as progress,
    ):
        for status in pool.imap_unordered(_migrate_funder, classic_funders):
            counts[status] += 1
            progress.set_postfix_str(
                f"✅ {counts['SUCCESS']} | ❌ {counts['FAILED']} | ➡️ {counts['SKIPPED']}"
            )
            progress.update(1)
