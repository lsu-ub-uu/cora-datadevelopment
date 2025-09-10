import xml.etree.ElementTree as ET
from typing import Union, Literal

XMLSpec = dict[str, "ChildSpec"]
ChildSpec = Union[Literal["text"], Literal["ignore"], XMLSpec]


class XMLValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def validate_xml(element: ET.Element, spec: XMLSpec) -> None:
    """
    Validate that the given XML element does not contain unknown tags, according to the provided specification.

    Raises XMLValidationError if the element does not conform to the spec.

    All tags are handled as optional.

    Example spec:
    ```
    {
        "child1": "text",  # Text node
        "child2": { # Nested element
            "subchild1": "text",
            "subchild2": "text"
        }
    }
    ```
    """

    def validate_element(element: ET.Element, spec: XMLSpec) -> list[str]:
        errors: list[str] = []

        for child in element:
            child_spec = spec.get(child.tag)

            if child_spec is None:
                # Unknown child tag
                errors.append(
                    f"Unknown child element <{child.tag}> found in <{element.tag}>"
                )
                continue

            if child_spec == "ignore":
                # Child is ignored
                continue

            if child_spec == "text" and len(child):
                # Child is text node
                errors.append(
                    f"Expected text content in <{child.tag}>, but found child elements"
                )
                continue

            if child_spec != "text":
                # Child is a group
                if len(child) == 0 and child.text is not None:
                    errors.append(
                        f"Expected child elements in <{child.tag}>, but found text content"
                    )
                    continue

                child_errors = validate_element(child, child_spec)
                errors.extend(child_errors)
        return errors

    errors = validate_element(element, spec)
    if len(errors) > 0:
        raise XMLValidationError("\n".join(errors))
