import xml.etree.ElementTree as ET

def create_degree_granting_institution(source_record: ET.Element) -> ET.Element:
    organisation_name = source_record.findtext(".//grantingInstitution/organisationName/name")
    degree_granting_institution = ET.Element("degreeGrantingInstitution", type="corporate")
    name_part = ET.SubElement(degree_granting_institution, "namePart")
    name_part.text = organisation_name
    role = ET.SubElement(degree_granting_institution, "role")
    role_term_element = ET.SubElement(role, "roleTerm")
    role_term_element.text = "dgg"
    print(ET.tostring(degree_granting_institution))
    return degree_granting_institution
