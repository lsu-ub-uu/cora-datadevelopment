import unittest
from common.CommonData import CommonData
import xml.etree.ElementTree as ET

class Test(unittest.TestCase):


    def setUp(self):
        self.common_data = CommonData()


    def tearDown(self):
        pass

    def test_create_record_info(self):
        record_info = self.common_data.create_record_info("someRecordType")
        
        expected_xml = """
                        <recordInfo>
                            <validationType>
                                <linkedRecordType>validationType</linkedRecordType>
                                <linkedRecordId>diva-someRecordType</linkedRecordId>
                            </validationType>
                            <dataDivider>
                                <linkedRecordType>system</linkedRecordType>
                                <linkedRecordId>divaData</linkedRecordId>
                            </dataDivider>
                        </recordInfo>
                        """
        self.assert_equal_for_xml_and_xml_string(record_info, expected_xml)
        
    def assert_equal_for_xml_and_xml_string(self, record_info, expected_xml):
        expected_as_xml = ET.fromstring(expected_xml)
        expected_normalized = self.normalize_xml_string(expected_as_xml)
        record_info_normalized = self.normalize_xml_string(record_info)
        self.assertEqual(record_info_normalized, expected_normalized)
        
    def normalize_xml_string(self, xml):
        if isinstance(xml, str):
            root = ET.fromstring(xml)
        else:
            root = xml  # already an Element
    
        def canonicalize(elem):
            attribs = ' '.join(f'{k}="{v}"' for k, v in sorted(elem.attrib.items()))
            start_tag = f"<{elem.tag}{(' ' + attribs) if attribs else ''}>"
    
            text = (elem.text or '').strip()
            children = ''.join(canonicalize(child) for child in elem)
            end_tag = f"</{elem.tag}>"
    
            return f"{start_tag}{text}{children}{end_tag}"
    
        return canonicalize(root)
if __name__ == "__main__":
    unittest.main()