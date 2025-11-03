import xml.etree.ElementTree as ET
from fedora_to_cora.transform.patent.create_date_other_type_patent import (
    create_date_other_type_patent,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_date_other_type_patent():
    source_record = ET.fromstring(
        """
        <publication>
            <patentDate>2022-12-24T00:00:00.000+01:00</patentDate>
        </publication>
        """
    )

    date = create_date_other_type_patent(source_record)

    assert_equal_for_xml_and_xml_string(
        date,
        """
        <dateOther type="patent">
            <year>2022</year>
            <month>12</month>
            <day>24</day>
        </dateOther>
        """,
    )
