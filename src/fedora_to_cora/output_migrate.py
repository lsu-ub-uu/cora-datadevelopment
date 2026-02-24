from typing import Literal
import xml.etree.ElementTree as ET
from common.xml_utils import pretty_print_xml
from common.xml_validate import validate_xml, XMLValidationError
from cora.context import Context
from cora.delete import delete_record
from fedora_to_cora.attachments_migrate import attachments_migrate
from fedora_to_cora.output_transform import transform_to_cora_output
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from fedora_to_cora.transform.transform_output_to_classic_quality import (
    transform_output_to_classic_quality,
)
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec


class OutputMigrationResult:
    pid: str
    status: Literal[
        "SUCCESS", "CLASSIC_QUALITY", "FAILED", "SKIPPED", "INPUT_VALIDATION_FAILED"
    ]
    errors: list[str] | None

    def __init__(
        self,
        pid: str,
        status: Literal[
            "SUCCESS", "CLASSIC_QUALITY", "FAILED", "SKIPPED", "INPUT_VALIDATION_FAILED"
        ],
        errors: list[str] | None = None,
    ):
        self.pid = pid
        self.status = status
        self.errors = errors


def output_migrate(
    source_record: ET.Element,
    context: Context,
    apply: bool = False,
    with_binaries: bool = False,
) -> OutputMigrationResult:
    """
    Migrates a Fedora XML publication record and its attached binaries to Cora.
    """
    pid = source_record.findtext("./pid")
    assert pid is not None

    try:
        validate_xml(source_record, fedora_publication_xml_spec)
    except XMLValidationError as e:
        error_str = f"XML validation error for record with publication type {source_record.findtext('./publicationType/publicationTypeCode')} and subtype {source_record.findtext('./subtype/publicationSubtypeCode')}: {e}"
        return OutputMigrationResult(
            pid, status="INPUT_VALIDATION_FAILED", errors=[error_str]
        )

    cora_output = transform_to_cora_output(source_record, context)

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )

    if not valid:
        return _handle_invalid_record(errors, pid, cora_output, context)
    if apply:
        create_record_result = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

        if not is_success_result(create_record_result):
            return OutputMigrationResult(
                pid,
                status="FAILED",
                errors=(
                    [create_record_result.error] if create_record_result.error else []
                ),
            )

        if with_binaries:
            success, errors = attachments_migrate(
                source_record,
                create_record_result.response_data,
                context,
            )
            if not success:
                context.log(
                    f"❌ Failed to migrate attachments for record with old id {source_record.findtext('.//pid')} Rolling back.",
                    level="error",
                )
                delete_record(create_record_result.response_data, context)
                return OutputMigrationResult(
                    pid,
                    status="FAILED",
                    errors=errors,
                )

    return OutputMigrationResult(pid, status="SUCCESS")


def _handle_invalid_record(
    errors: list[str] | None, pid: str, cora_output: ET.Element, context: Context
) -> OutputMigrationResult:
    if _has_duplicate_old_id(errors, pid):
        return OutputMigrationResult(
            pid,
            status="SKIPPED",
            errors=["A record with the same oldId already exists in the system"],
        )

    classic_quality_record = transform_output_to_classic_quality(cora_output, errors)
    context.log(
        f"Creating classic quality record for old id {pid}:\n{pretty_print_xml(classic_quality_record)}",
        level="warning",
    )
    create_result = create_record(
        classic_quality_record,
        record_type="diva-output",
        context=context,
    )
    if is_success_result(create_result):
        return OutputMigrationResult(pid, status="CLASSIC_QUALITY", errors=errors)
    else:
        context.log(
            f"❌ Failed to create classic quality record for old id {pid}. {create_result.error}",
            level="error",
        )

        return OutputMigrationResult(
            pid,
            status="FAILED",
            errors=[create_result.error] if create_result.error is not None else [],
        )


def _has_duplicate_old_id(errors: list[str] | None, old_id: str) -> bool:
    return errors is not None and any(
        error
        == f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
        for error in errors
    )
