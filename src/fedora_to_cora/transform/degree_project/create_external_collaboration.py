import xml.etree.ElementTree as ET


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
) -> ET.Element:
    external_collaboration = ET.Element("externalCollaboration")

    for i, partner in enumerate(partners):
        name_part = ET.SubElement(external_collaboration, "namePart", repeatId=str(i))
        name_part.text = partner.text

    return external_collaboration


def _create_external_collaboration_default() -> ET.Element:
    external_collaboration = ET.Element("externalCollaboration")
    name_part = ET.SubElement(external_collaboration, "namePart", repeatId="0")
    name_part.text = "Externt samarbete"
    return external_collaboration
