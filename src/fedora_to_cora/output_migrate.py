from typing import Literal
import xml.etree.ElementTree as ET
from cora.context import Context
from cora.delete import delete_record
from fedora_to_cora.attachments_migrate import attachments_migrate
from fedora_to_cora.output_transform import transform_to_cora_output
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from common.xml_utils import pretty_print_xml


class OutputMigrationResult:
    status: Literal["SUCCESS", "CLASSIC_QUALITY", "FAILED"]
    errors: list[str] | None

    def __init__(
        self,
        status: Literal["SUCCESS", "CLASSIC_QUALITY", "FAILED"],
        errors: list[str] | None = None,
    ):
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

    cora_output = transform_to_cora_output(source_record, context)

    valid, errors = validate_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )

    if not valid:
        create_result = _create_classic_quality_record(cora_output, context)
        if is_success_result(create_result):
            return OutputMigrationResult(status="CLASSIC_QUALITY", errors=errors)
        else:
            return OutputMigrationResult(
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
                    status="FAILED",
                    errors=errors,
                )

    return OutputMigrationResult(status="SUCCESS")


def _create_classic_quality_record(cora_output: ET.Element, context: Context):
    validation_type_link = cora_output.find(
        "./recordInfo/validationType/linkedRecordId"
    )
    assert validation_type_link is not None and validation_type_link.text is not None
    validation_type_link.text = "classic_" + validation_type_link.text
    data_quality = cora_output.find("./dataQuality")
    assert data_quality is not None
    data_quality.text = "classic"

    for index, child in enumerate(cora_output):
        add_repeat_ids(child, index)

    return create_record(
        cora_output,
        record_type="diva-output",
        context=context,
    )


def add_repeat_ids(element: ET.Element, repeat_id: int = 0):

    if element.get("repeatId") is None:
        element.set("repeatId", str(repeat_id))

    if len(element) > 0:
        if element.tag == "recordInfo":
            return

        for index, child in enumerate(element):
            add_repeat_ids(child, index)


if __name__ == "__main__":
    el = ET.fromstring(
        """
        <record>
            <recordInfo>
                <item>Value1</item>
                <item>Value2</item>
            </recordInfo>
            <group repeatId="23123">
                <item>Value1</item>
                <item>Value2</item>
            </group>
            <single>Value3</single>
        </record>
        """
    )
    add_repeat_ids(el)

    print(pretty_print_xml(el))
