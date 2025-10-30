from fedora_to_cora.transform.create_origin_info import create_origin_info
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_origin_info_date_issued():
    source_record = ET.fromstring(
        """
        <publication>
            <dateIssued>2022</dateIssued>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record, MockContext())

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


def test_origin_info_date_issued_missing_year():
    source_record = ET.fromstring(
        """
        <publication>
            <dateIssued></dateIssued>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
        <originInfo></originInfo>
        """,
    )


def test_create_agent_from_uncontrolled_publisher():
    source_record = ET.fromstring(
        """
        <publication>
            <publisher>
                <publisherName>Uppsala Läroverk</publisherName>
            </publisher>
        </publication>
    """
    )

    agent = create_origin_info(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        agent,
        """
        <originInfo>
            <agent repeatId="0">
                <namePart>Uppsala Läroverk</namePart>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </agent>
        </originInfo>
        """,
    )


def test_create_agent_from_controlled_publisher(monkeypatch):
    mock_old_id = "985"
    expected_cora_id = "diva-publisher:21861441014837120"
    mock_context = MockContext()

    def mock_get_pub(old_id, *args, **kwargs):
        if old_id == mock_old_id:
            return expected_cora_id
        else:
            return None

    monkeypatch.setattr(
        "fedora_to_cora.transform.create_origin_info.get_cora_id_by_old_id",
        mock_get_pub,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
            <publisher>
                <publishingHouse>
                    <publishingHouseId>{mock_old_id}</publishingHouseId>
                </publishingHouse>
            </publisher>
        </publication>
        """
    )

    agent = create_origin_info(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        agent,
        f""" 
        <originInfo>
            <agent repeatId="0">
                <publisher>
                    <linkedRecordType>diva-publisher</linkedRecordType>
                    <linkedRecordId>{expected_cora_id}</linkedRecordId>
                </publisher>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </agent>
        </originInfo>
        """,
    )


def test_create_place_from_city():
    source_record = ET.fromstring(
        """
        <publication>
            <publisher>
                <city>Uppsala</city>
            </publisher>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
        <originInfo>
            <place repeatId="0">
                <placeTerm>Uppsala</placeTerm>
            </place>
        </originInfo>
        """,
    )


def test_create_editon():
    source_record = ET.fromstring(
        """
        <publication>
            <edition>First Edition</edition>
        </publication>
        """
    )

    origin_info = create_origin_info(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        origin_info,
        """
        <originInfo>
            <edition>First Edition</edition>
        </originInfo>
        """,
    )
