from xml.etree import ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.patent.create_patent_holder import create_patent_holder


def test_create_patent_holder():
    source_record = ET.fromstring(
        """
    <publication>
        <patentOrganisation>Patentorganisation</patentOrganisation>
    </publication>
    """
    )
    patent_country = create_patent_holder(source_record)

    assert_equal_for_xml_and_xml_string(
        patent_country,
        """
            <name type="corporate" otherType="patentHolder">
                <namePart>Patentorganisation</namePart>
                <role>
                    <roleTerm>pth</roleTerm>
                </role>
            </name>
        """,
    )


def test_empty_patent_organisation():
    source_xml = ET.fromstring(
        """
        <publication>
            <patentOrganisation></patentOrganisation>
        </publication>
    """
    )

    patent_holder = create_patent_holder(source_xml)

    assert patent_holder is None


def test_missing_patent_organisation():
    source_xml = ET.fromstring(
        """
        <publication>
        </publication>
    """
    )

    patent_holder = create_patent_holder(source_xml)

    assert patent_holder is None
