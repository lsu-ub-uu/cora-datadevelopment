from dataclasses import dataclass
import xml.etree.ElementTree as ET
from classic.get_authority_person import get_authority_person
from cora.context import Context
from fedora_to_cora.authority_person_json_validate import (
    AuthorityPersonJSONValidationError,
    validate_authority_person_json,
)
from fedora_to_cora.transform_person import transform_person
from cora.create import create_record, is_success_result
from typing import Literal


@dataclass
class MigratePersonResult:
    status: Literal["CREATED", "SKIPPED", "FAILED"]
    cora_person_id: str | None
    error: str | None


def migrate_person(authority_pid: str, context: Context) -> MigratePersonResult:
    try:
        person = get_authority_person(authority_pid)
    except Exception as e:
        return MigratePersonResult(
            "FAILED", None, f"Failed to fetch authority person: {e}"
        )

    try:
        validate_authority_person_json(person)
    except AuthorityPersonJSONValidationError as e:
        return MigratePersonResult("FAILED", None, f"JSON validation error: {e}")

    transformed_person = transform_person(person, context)

    create_result = create_record(
        transformed_person, context=context, record_type="diva-person"
    )

    if not is_success_result(create_result):
        if _record_already_exists(create_result.error, authority_pid):
            return MigratePersonResult(
                "SKIPPED", None, "Cora diva-person record already exists"
            )
        return MigratePersonResult(
            "FAILED", None, f"Failed to create person record: {create_result.error}"
        )

    return MigratePersonResult("CREATED", create_result.record_id, None)


def _record_already_exists(error_message: str, authority_pid: str) -> bool:
    return (
        error_message
        == f"The record could not be created as it fails unique validation with the following 1 error messages: [A record matching the unique rule with [key: oldId, value: {authority_pid}] already exists in the system]"
    )
