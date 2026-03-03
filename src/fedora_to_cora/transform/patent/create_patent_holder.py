import xml.etree.ElementTree as ET

from common.xml_utils import create_group, create_text


def create_patent_holder(source_record: ET.Element) -> ET.Element | None:
    patent_organisation = source_record.findtext("patentOrganisation")
    if patent_organisation is None or patent_organisation.strip() == "":
        return None
    return create_group(
        "name",
        type="corporate",
        otherType="patentHolder",
        children=[
            create_text("namePart", patent_organisation),
            create_group("role", [create_text("roleTerm", "pth")]),
        ],
    )
