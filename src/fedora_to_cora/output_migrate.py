from typing import Literal
import xml.etree.ElementTree as ET
from common.xml_utils import pretty_print_xml
from cora.context import Context
from cora.delete import delete_record
from fedora_to_cora.attachments_migrate import attachments_migrate
from fedora_to_cora.output_transform import transform_to_cora_output
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from fedora_to_cora.transform.transform_output_to_classic_quality import (
    transform_output_to_classic_quality,
)


class OutputMigrationResult:
    pid: str
    status: Literal["SUCCESS", "CLASSIC_QUALITY", "FAILED"]
    errors: list[str] | None

    def __init__(
        self,
        pid: str,
        status: Literal["SUCCESS", "CLASSIC_QUALITY", "FAILED"],
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

    cora_output = transform_to_cora_output(source_record, context)

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )

    if not valid:
        classic_quality_record = transform_output_to_classic_quality(
            cora_output, errors
        )
        context.log(
            f"Creating classic quality record for old id {source_record.findtext('.//pid')}:\n{pretty_print_xml(classic_quality_record)}",
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
            return OutputMigrationResult(
                pid,
                status="FAILED",
                errors=(errors or [])
                + ([create_result.error] if create_result.error is not None else []),
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
