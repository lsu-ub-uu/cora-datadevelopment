import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_artistic_work import create_artistic_work
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_artistic_work():
    source_record = ET.fromstring(
        """
        <publication>
            <artisticWork>true</artisticWork>
        </publication>
        """
    )

    artistic_work = create_artistic_work(source_record)

    assert_equal_for_xml_and_xml_string(
        artistic_work, "<artisticWork type='outputType'>true</artisticWork>"
    )


def test_create_artistic_work_false():
    source_record = ET.fromstring(
        """
        <publication>
            <artisticWork>false</artisticWork>
        </publication>
        """
    )

    artistic_work = create_artistic_work(source_record)

    assert_equal_for_xml_and_xml_string(
        artistic_work, "<artisticWork type='outputType'>false</artisticWork>"
    )


def test_create_artistic_work_missing():
    source_record = ET.fromstring(
        """
        <publication>
        </publication>
        """
    )

    artistic_work = create_artistic_work(source_record)

    assert artistic_work is None
