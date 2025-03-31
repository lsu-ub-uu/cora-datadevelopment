import xml.etree.ElementTree as ET
class  CommonData:

    @staticmethod
    def read_source_xml(filePath_sourceXml):
        sourceFile_xml = ET.parse(filePath_sourceXml)
        root = sourceFile_xml.getroot()
        return root
    
    @staticmethod
    def remove_action_link(element):
        for actionLinks in element.findall('actionLinks'):
            element.remove(actionLinks)

    @staticmethod
    def remove_actionLinks_from_record(record):
        for clean_record in record.findall('.//series'):
            for validationType in clean_record.findall('.//validationType'):
                CommonData.remove_action_link(validationType)
            for dataDivider in clean_record.findall('.//dataDivider'):
                CommonData.remove_action_link(dataDivider)
            for type in clean_record.findall('.//type'):
                CommonData.remove_action_link(type)
            for createdBy in clean_record.findall('.//createdBy'):
                CommonData.remove_action_link(createdBy)
            for updatedBy in clean_record.findall('.//updatedBy'):
                CommonData.remove_action_link(updatedBy)
        return clean_record

