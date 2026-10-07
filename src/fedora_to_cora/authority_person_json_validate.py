from typing import Any

from fedora_to_cora.fedora_authority_person_spec import (
    fedora_authority_person_alternative_name_spec,
    fedora_authority_person_affiliation_spec,
    fedora_authority_person_organisation_spec,
    fedora_authority_person_spec,
)

JSONSpec = dict[str, Any]

_organisation_spec: JSONSpec = {
    **fedora_authority_person_organisation_spec,
}
_organisation_spec["parents"] = [_organisation_spec]

_affiliation_spec: JSONSpec = {
    **fedora_authority_person_affiliation_spec,
    "parents": [_organisation_spec],
}

_authority_person_spec: JSONSpec = {
    **fedora_authority_person_spec,
    "alternativeNames": [fedora_authority_person_alternative_name_spec],
    "identifiers": [fedora_authority_person_spec["identifiers"]],
    "affiliations": [_affiliation_spec],
    "urls": [fedora_authority_person_spec["urls"]],
    "recordInfo": {
        "events": [
            {
                "type": "$ANY_TEXT$",
                "timestamp": "$ANY_TEXT$",
                "name": "$ANY_TEXT$",
                "userId": "$ANY_TEXT$",
                "ip": "$ANY_TEXT$",
            }
        ],
        "recordDeleted": "$BOOLEAN$",
    },
}

_document_spec: JSONSpec = {"authorityPerson": _authority_person_spec}


class AuthorityPersonJSONValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def validate_authority_person_json(document: Any) -> None:
    """Validate an authority-person JSON document against its known fields."""
    if not isinstance(document, dict):
        raise AuthorityPersonJSONValidationError("Expected a JSON object at root")

    if "authorityPerson" not in document:
        raise AuthorityPersonJSONValidationError(
            "Missing required property 'authorityPerson' at root"
        )

    errors = _validate_object(document, _document_spec, "root")
    if errors:
        raise AuthorityPersonJSONValidationError("\n".join(errors))


def _validate_object(value: Any, spec: JSONSpec, path: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"Expected a JSON object at {path}"]

    errors = []
    for key, child in value.items():
        child_spec = spec.get(key)
        child_path = f"{path}.{key}"
        if child_spec is None:
            errors.append(f"Unknown property '{key}' at {path}")
        elif isinstance(child_spec, list):
            if not isinstance(child, list):
                errors.append(f"Expected a JSON array at {child_path}")
            else:
                item_spec = child_spec[0]
                for index, item in enumerate(child):
                    errors.extend(
                        _validate_object(item, item_spec, f"{child_path}[{index}]")
                    )
        elif isinstance(child_spec, dict):
            if isinstance(child, list):
                errors.append(f"Expected a JSON object at {child_path}")
                continue
            errors.extend(_validate_object(child, child_spec, child_path))
        elif child_spec == "$BOOLEAN$":
            if not isinstance(child, bool):
                errors.append(f"Expected a JSON boolean at {child_path}")
        elif child_spec == "$NUMBER$":
            if isinstance(child, bool) or not isinstance(child, (int, float)):
                errors.append(f"Expected a JSON number at {child_path}")
        elif not isinstance(child, str):
            errors.append(f"Expected a JSON string at {child_path}")
    return errors
