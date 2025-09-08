import xml.etree.ElementTree as ET
from typing import Union, Literal

XMLSpec = dict[str, "ChildSpec"]
ChildSpec = Union[Literal["text"], XMLSpec]


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
    for child in element:
        child_spec = spec.get(child.tag)
        if child_spec is None:
            raise XMLValidationError(
                f"Unknown child element <{child.tag}> found in <{element.tag}>"
            )
        if child_spec == "text" and len(child):
            raise XMLValidationError(
                f"Expected text content in <{child.tag}>, but found child elements"
            )
        if child_spec != "text":
            if len(child) == 0 and child.text is not None:
                raise XMLValidationError(
                    f"Expected child elements in <{child.tag}>, but found text content"
                )
            validate_xml(child, child_spec)
