from typing import Literal, cast
import xml.etree.ElementTree as ET
import logging
from common.xml_utils import pretty_print_xml
from common.xml_validate import validate_xml, XMLValidationError
from cora.context import Context
from fedora_to_cora.output_migration_result import OutputMigrationResult
from cora.delete import delete_record
from fedora_to_cora.attachments_migrate import attachments_migrate
from fedora_to_cora.output_transform import transform_to_cora_output
from cora.validate import validate_record
from cora.create import create_record, is_success_result, CreateRecordFailureResult
from fedora_to_cora.transform.transform_output_to_classic_quality import (
    transform_output_to_classic_quality,
)
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec
from fedora_to_cora.create_relations import create_relations

logger = logging.getLogger(__name__)


def output_migrate(
    source_record: ET.Element,
    context: Context,
    apply: bool = False,
    with_binaries: bool = False,
    fedora_url: str = "",
) -> OutputMigrationResult:
    """
    Migrates a Fedora XML publication record and its attached binaries to Cora.
    """
    pid = source_record.findtext("./pid")
    publication_type = source_record.findtext("./publicationType/publicationTypeCode")
    cora_id = None
    relations = []
    assert pid is not None

    try:
        validate_xml(source_record, fedora_publication_xml_spec)
    except XMLValidationError as e:
        return OutputMigrationResult(
            pid,
            publication_type,
            status="INPUT_VALIDATION_FAILED",
            errors=[str(e)],
        )

    cora_output = transform_to_cora_output(source_record, context)

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )
    if not valid:
        return _handle_failed_cora_validation(
            errors,
            pid,
            publication_type,
            source_record,
            cora_output,
            context,
            apply,
            with_binaries,
        )

    if apply:
        create_record_result = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

        if is_success_result(create_record_result):
            cora_id = create_record_result.record_id
            relations = create_relations(source_record)
        else:
            return OutputMigrationResult(
                pid,
                publication_type,
                status="FAILED",
                errors=(
                    [create_record_result.error] if create_record_result.error else []
                ),
            )

        if with_binaries:
            success, errors = _migrate_attachments_with_rollback(
                source_record,
                create_record_result.response_data,
                context,
                fedora_url=fedora_url,
            )
            if not success:
                return OutputMigrationResult(
                    pid,
                    publication_type=publication_type,
                    status="FAILED",
                    errors=errors,
                )

    return OutputMigrationResult(
        pid,
        publication_type=publication_type,
        status="SUCCESS",
        cora_id=cora_id,
        relations=relations,
    )


def _migrate_attachments_with_rollback(
    source_record: ET.Element,
    created_record: ET.Element,
    context: Context,
    *,
    fedora_url: str = "",
) -> tuple[bool, list[str] | None]:
    success, errors = attachments_migrate(
        source_record,
        created_record,
        context,
        fedora_url=fedora_url,
    )

    if not success:
        logger.error(
            f"❌ Failed to migrate attachments for record with old id {source_record.findtext('.//pid')} Rolling back."
        )
        delete_record(created_record, context)

    return success, errors


def _handle_failed_cora_validation(
    errors: list[str] | None,
    pid: str,
    publication_type: str | None,
    source_record: ET.Element,
    cora_output: ET.Element,
    context: Context,
    apply: bool,
    with_binaries: bool = False,
) -> OutputMigrationResult:
    if _has_duplicate_old_id(errors, pid):
        return OutputMigrationResult(
            pid,
            publication_type,
            status="SKIPPED",
            errors=["A record with the same oldId already exists in the system"],
        )

    return _migrate_record_as_classic_quality(
        errors,
        pid,
        publication_type,
        source_record,
        cora_output,
        context,
        apply,
        with_binaries,
    )


def _migrate_record_as_classic_quality(
    errors: list[str] | None,
    pid: str,
    publication_type: str | None,
    source_record: ET.Element,
    cora_output: ET.Element,
    context: Context,
    apply: bool,
    with_binaries: bool = False,
) -> OutputMigrationResult:
    classic_quality_record = transform_output_to_classic_quality(cora_output, errors)

    if not apply:
        logger.warning(
            f"Validating classic quality record for old id {pid}:\n{pretty_print_xml(classic_quality_record)}"
        )
        return _dry_run_classic_quality_migration(
            classic_quality_record, pid, publication_type, context, errors
        )
    else:
        logger.warning(
            f"Creating classic quality record for old id {pid}:\n{pretty_print_xml(classic_quality_record)}"
        )
        return _apply_classic_quality_migration(
            classic_quality_record,
            pid,
            publication_type,
            context,
            errors,
            source_record=source_record,
            with_binaries=with_binaries,
        )


def _dry_run_classic_quality_migration(
    classic_quality_record: ET.Element,
    pid: str,
    publication_type: str | None,
    context: Context,
    errors: list[str] | None,
) -> OutputMigrationResult:
    classic_valid, classic_errors = validate_record(
        classic_quality_record,
        record_type="diva-output",
        context=context,
    )
    if classic_valid:
        return OutputMigrationResult(
            pid,
            publication_type,
            status="CLASSIC_QUALITY",
            errors=errors,
        )
    return OutputMigrationResult(
        pid,
        publication_type,
        status="FAILED",
        errors=classic_errors,
    )


def _apply_classic_quality_migration(
    classic_quality_record: ET.Element,
    pid: str,
    publication_type: str | None,
    context: Context,
    errors: list[str] | None,
    *,
    source_record: ET.Element,
    with_binaries: bool = False,
):
    create_result = create_record(
        classic_quality_record,
        record_type="diva-output",
        context=context,
    )
    if is_success_result(create_result):
        if with_binaries:
            success, attachment_errors = _migrate_attachments_with_rollback(
                source_record,
                create_result.response_data,
                context,
            )
            if not success:

                return OutputMigrationResult(
                    pid,
                    publication_type,
                    status="FAILED",
                    errors=attachment_errors,
                )
        return OutputMigrationResult(
            pid,
            publication_type,
            status="CLASSIC_QUALITY",
            errors=errors,
            cora_id=create_result.record_id,
            relations=create_relations(classic_quality_record),
        )
    else:
        if _create_failed_due_to_duplicate(create_result, pid):
            return OutputMigrationResult(
                pid,
                publication_type,
                status="SKIPPED",
                errors=["A record with the same oldId already exists in the system"],
            )
        logger.error(
            f"❌ Failed to create classic quality record for old id {pid}. {create_result.error}"
        )
        return OutputMigrationResult(
            pid,
            publication_type,
            status="FAILED",
            errors=[create_result.error] if create_result.error is not None else [],
        )


def _has_duplicate_old_id(errors: list[str] | None, old_id: str) -> bool:
    logger.info(
        f"➡️ Skipped record with oldId {old_id} due to duplicate record found when creating classic quality record. Errors: {errors}"
    )
    return errors is not None and any(
        error
        == f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
        for error in errors
    )


def _create_failed_due_to_duplicate(
    create_result: CreateRecordFailureResult, old_id: str
) -> bool:
    return create_result.status == 409 and (
        f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
        in create_result.error
    )
