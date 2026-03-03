import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text, create_text


def create_external_collaboration(source_record: ET.Element) -> ET.Element | None:
    """
    Create an external collaboration element from the source record.

    Args:
        source_record (ET.Element): The source XML element containing external cooperation data.

    Returns:
        ET.Element: The created external collaboration XML element.
    """
    external = source_record.findtext("./externalCooperation/external")
    partners = source_record.findall("./externalCooperation/partners/partner/name")

    if external == "true" and len(partners) == 0:
        return _create_external_collaboration_default()
    elif len(partners) > 0:
        return _create_external_collaboration_from_partners(partners)

    return None


def _create_external_collaboration_from_partners(
    partners: list[ET.Element],
):
    return create_group(
        "externalCollaboration",
        children=[
            create_text("namePart", partner.text, repeatId=str(i))
            for i, partner in enumerate(partners)
        ],
    )


def _create_external_collaboration_default() -> ET.Element | None:
    return create_group(
        "externalCollaboration",
        [create_text("namePart", "Externt samarbete", repeatId="0")],
    )
