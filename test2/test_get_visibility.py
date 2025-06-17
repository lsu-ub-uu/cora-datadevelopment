import xml.etree.ElementTree as ET
from fedora_to_cora.get_visibility import get_visibility

def test_return_published_when_last_update_is_PUBLISHED():
    test_element = ET.Element("publication")
    administrativeInfo = ET.SubElement(test_element, "administrativeInfo")
    updaters = ET.SubElement(administrativeInfo, "updaters")

    userInformation1 = ET.SubElement(updaters, "userInformation")
    userAction1 = ET.SubElement(userInformation1, "userAction")
    userAction1.text = "UNPUBLISHED"

    userInformation2 = ET.SubElement(updaters, "userInformation")
    userAction2 = ET.SubElement(userInformation2, "userAction")
    userAction2.text = "PUBLISHED"

    print(ET.tostring(test_element, encoding="utf-8", method="xml"))

    assert get_visibility(test_element) == "published"

