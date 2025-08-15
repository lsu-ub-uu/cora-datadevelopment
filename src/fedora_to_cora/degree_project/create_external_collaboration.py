import xml.etree.ElementTree as ET

def create_external_collaboration(source_record: ET.Element) -> ET.Element:
    """
    Create an external collaboration element from the source record.
    
    Args:
        source_record (ET.Element): The source XML element containing external cooperation data.
    
    Returns:
        ET.Element: The created external collaboration XML element.
    """
    external_collaboration = ET.Element("externalCollaboration")
    
    for i, partner in enumerate(source_record.findall("./externalCooperation/partners/partner")):
        name_part = ET.SubElement(external_collaboration, "namePart", repeatId=str(i))
        name_part.text = partner.findtext("name", "")
    
    return external_collaboration