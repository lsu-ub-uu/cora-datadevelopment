import xml.etree.ElementTree as ET
class  CommonData:

    @staticmethod
    def read_source_xml(filePath_sourceXml):
        sourceFile_xml = ET.parse(filePath_sourceXml)
        root = sourceFile_xml.getroot()
        return root