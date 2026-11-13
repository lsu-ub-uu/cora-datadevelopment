from dataclasses import dataclass
import xml.etree.ElementTree as ET
from classic.get_authority_person import get_authority_person
from common.xml_utils import pretty_print_xml
from cora_python_client import CoraClient, CoraError, CoraConflictError
from fedora_to_cora.transform_person import transform_person
from cora.create import create_record, is_success_result
from typing import Literal
import logging

logger = logging.getLogger(__name__)


@dataclass
class MigratePersonResult:
    status: Literal["CREATED", "SKIPPED", "FAILED"]
    cora_person_id: str | None
    error: str | None


def migrate_person(authority_pid: str, cora_client: CoraClient) -> MigratePersonResult:
    try:
        created_person = get_authority_person(authority_pid)
    except Exception as e:
        return MigratePersonResult(
            "FAILED", None, f"Failed to fetch authority person: {e}"
        )

    if _is_hidden_person(created_person):
        return MigratePersonResult(
            "SKIPPED", None, "Skipped non-public authority record"
        )

    try:
        transformed_person = transform_person(created_person, cora_client)
    except Exception as e:
        return MigratePersonResult("FAILED", None, f"Failed to transform person: {e}")

    try:
        created_person = cora_client.create_record(
            transformed_person, record_type="diva-person"
        )
    except CoraError as error:
        if _is_duplicate_record_error(error, authority_pid):
            return MigratePersonResult(
                "SKIPPED", None, "Cora diva-person record already exists"
            )
        logger.error(
            f"Failed to create person record: {error}. Data:\n{pretty_print_xml(transformed_person)}"
        )
        return MigratePersonResult(
            "FAILED", None, f"Failed to create person record: {error}"
        )

    return MigratePersonResult("CREATED", created_person.id, None)


def _is_duplicate_record_error(error: CoraError, authority_pid: str) -> bool:
    return isinstance(error, CoraConflictError) and (
        f"A record matching the unique rule with [key: oldId, value: {authority_pid}] already exists in the system"
        in error.message
    )


def _is_hidden_person(person: dict) -> bool:
    return not person["authorityPerson"]["publicRecord"]
