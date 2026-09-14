from typing import Literal, cast
import xml.etree.ElementTree as ET
import logging
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

OutputMigrationStatus = Literal[
    "SUCCESS",
    "CLASSIC_QUALITY",
    "FAILED",
    "SKIPPED",
    "INPUT_VALIDATION_FAILED",
]
logger = logging.getLogger(__name__)


class OutputMigrationResult:
    pid: str
    publication_type: str
    status: OutputMigrationStatus
    errors: list[str] | None

    def __init__(
        self,
        pid: str,
        publication_type: str | None = None,
        status: OutputMigrationStatus | None = None,
        errors: list[str] | None = None,
    ):
        if status is None and isinstance(publication_type, str):
            valid_statuses = {
                "SUCCESS",
                "CLASSIC_QUALITY",
                "FAILED",
                "SKIPPED",
                "INPUT_VALIDATION_FAILED",
            }
            if publication_type in valid_statuses:
                status = cast(OutputMigrationStatus, publication_type)
                publication_type = "UNKNOWN"

        assert status is not None

        self.pid = pid
        self.publication_type = publication_type if publication_type else "UNKNOWN"
        self.status = status
        self.errors = errors


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
    assert pid is not None

    try:
        validate_xml(source_record, fedora_publication_xml_spec)
    except XMLValidationError as e:
        error_str = str(e)
        return OutputMigrationResult(
            pid,
            publication_type,
            status="INPUT_VALIDATION_FAILED",
            errors=[error_str],
        )

    cora_output = transform_to_cora_output(source_record, context)

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )

    if not valid:
        return _handle_invalid_record(
            errors, pid, publication_type, cora_output, context
        )
    if apply:
        create_record_result = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

        if not is_success_result(create_record_result):
            return OutputMigrationResult(
                pid,
                publication_type,
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
                fedora_url=fedora_url,
            )
            if not success:
                logger.error(
                    f"❌ Failed to migrate attachments for record with old id {source_record.findtext('.//pid')} Rolling back."
                )
                delete_record(create_record_result.response_data, context)
                return OutputMigrationResult(
                    pid,
                    publication_type=publication_type,
                    status="FAILED",
                    errors=errors,
                )

    return OutputMigrationResult(
        pid, publication_type=publication_type, status="SUCCESS"
    )


def _handle_invalid_record(
    errors: list[str] | None,
    pid: str,
    publication_type: str | None,
    cora_output: ET.Element,
    context: Context,
) -> OutputMigrationResult:
    if _has_duplicate_old_id(errors, pid):
        return OutputMigrationResult(
            pid,
            publication_type,
            status="SKIPPED",
            errors=["A record with the same oldId already exists in the system"],
        )

    classic_quality_record = transform_output_to_classic_quality(cora_output, errors)
    logger.warning(
        f"Creating classic quality record for old id {pid}:\n{pretty_print_xml(classic_quality_record)}"
    )
    create_result = create_record(
        classic_quality_record,
        record_type="diva-output",
        context=context,
    )
    if is_success_result(create_result):
        return OutputMigrationResult(
            pid, publication_type, status="CLASSIC_QUALITY", errors=errors
        )
    else:
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
    return errors is not None and any(
        error
        == f"A record matching the unique rule with [key: oldId, value: {old_id}] already exists in the system"
        for error in errors
    )
