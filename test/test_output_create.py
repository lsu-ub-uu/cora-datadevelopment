from helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.output_create import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml

def test_creates_ouput():
    fedora_xml =  read_source_xml("data/fedora_xml/1681782_varldskulturmuserna.xml")

    result = transform_to_cora_output(fedora_xml)


    assert result is not None, "The result should not be None"
