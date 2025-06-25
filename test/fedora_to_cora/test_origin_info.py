from fedora_to_cora import create_origin_info
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
import pytest


def test_origin_info():
    source_record = ET.fromstring(
        """
        <publication>
            <dateIssued>2022</dateIssued>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record)

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
        <originInfo>
            <dateIssued>
                <year>2022</year>
            </dateIssued>
        </originInfo>
        """,
    )


def test_origin_info_error_when_missing_year():
    source_record = ET.fromstring(
        """
        <publication>
            <dateIssued></dateIssued>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record)

    assert origin_info is None
