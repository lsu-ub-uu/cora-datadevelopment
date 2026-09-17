from common.xml_utils import create_group, create_text
from fedora_to_cora.output_migration_result import OutputMigrationResult
from typing import Literal
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from cora.update import update_record
from cora.get_record import get_record
from common.common_data import create_record_link


class OutputRelationMigrationResult:
    def __init__(
        self,
        status: Literal["NO_RELATIONS", "UPDATED", "FAILED"],
        pid: str,
        cora_id: str | None,
        error: str | None,
    ):
        self.pid = pid
        self.cora_id = cora_id
        self.status = status
        self.error = error


def migrate_output_relations(
    output_migration_result: OutputMigrationResult, context: Context
) -> OutputRelationMigrationResult:
    if len(output_migration_result.relations) == 0:
        return OutputRelationMigrationResult(
            status="NO_RELATIONS",
            pid=output_migration_result.pid,
            cora_id=output_migration_result.cora_id,
            error=None,
        )

    assert output_migration_result.cora_id is not None

    try:
        result = get_record(context, "diva-output", output_migration_result.cora_id)
        updated_xml = _add_relations(result, output_migration_result.relations, context)
        _try_to_update_record(updated_xml, context=context)
    except Exception as e:
        return OutputRelationMigrationResult(
            status="FAILED",
            pid=output_migration_result.pid,
            cora_id=output_migration_result.cora_id,
            error=str(e),
        )

    return OutputRelationMigrationResult(
        status="UPDATED",
        pid=output_migration_result.pid,
        cora_id=output_migration_result.cora_id,
        error=None,
    )


def _add_relations(record_xml, relations, context: Context):
    xml_relations = _transform_relations(relations, context)
    for rel in xml_relations:
        record_xml.find("./data/output").append(rel)
    return record_xml


def _transform_relations(relations, context: Context):
    return [
        _transform_relation(relation, context, repeat_id=str(index))
        for index, relation in enumerate(relations)
    ]


def _transform_relation(relation, context: Context, repeat_id: str):
    relation_cora_id = get_cora_id_by_old_id(
        relation.pid, record_type="diva-output", context=context
    )

    return create_group(
        "related",
        type="constituent" if relation.type == "constituent" else None,
        repeatId=repeat_id,
        children=[
            create_record_link(
                "output", record_type="diva-output", record_id=relation_cora_id
            )
        ],
    )


def _try_to_update_record(updated_xml, context: Context):
    result = update_record(updated_xml, context=context)
    if not result.success:
        raise Exception(f"Failed to update record: {result.error}")
