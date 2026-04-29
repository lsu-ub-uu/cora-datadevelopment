import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text, create_text


def create_external_collaborations(source_record: ET.Element) -> list[ET.Element]:
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
        return [_create_external_collaborations_default()]
    elif len(partners) > 0:
        return _create_external_collaborations_from_partners(partners)

    return []


def _create_external_collaborations_default():
    return _create_external_collaboration("Externt samarbete", repeat_id=0)


def _create_external_collaborations_from_partners(
    partners: list[ET.Element],
):
    return [
        _create_external_collaboration(partner.text, repeat_id=i)
        for i, partner in enumerate(partners)
        if partner.text and partner.text.strip() != ""
    ]


def _create_external_collaboration(name: str, repeat_id: int):
    external_collaboration = create_group(
        "name",
        type="corporate",
        otherType="externalCollaboration",
        repeatId=str(repeat_id),
        children=[
            create_group("role", children=[create_text("roleTerm", value="ctb")]),
            create_text("namePart", value=name),
        ],
    )

    assert external_collaboration is not None
    return external_collaboration
