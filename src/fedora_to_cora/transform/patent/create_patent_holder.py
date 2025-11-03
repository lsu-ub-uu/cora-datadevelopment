import xml.etree.ElementTree as ET


def create_patent_holder(source_record: ET.Element) -> ET.Element | None:
    patent_organisation = source_record.findtext("patentOrganisation")
    if patent_organisation is None or len(patent_organisation) == 0:
        return None

    patent_holder = ET.Element("patentHolder", type="corporate")
    ET.SubElement(patent_holder, "namePart").text = patent_organisation

    role = ET.SubElement(patent_holder, "role")
    ET.SubElement(role, "roleTerm").text = "pth"

    return patent_holder
