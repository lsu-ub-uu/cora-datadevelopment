from fedora_to_cora.transform.create_origin_info import create_origin_info
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_origin_info_date_issued():
    source_record = ET.fromstring("""
        <publication>
            <dateIssued>2022</dateIssued>
        </publication>
        """)

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
    source_record = ET.fromstring("""
        <publication>
            <dateIssued></dateIssued>
        </publication>
        """)

    origin_info = create_origin_info(source_record, MockContext())

    assert origin_info is None


def test_create_agent_from_uncontrolled_publisher():
    source_record = ET.fromstring("""
        <publication>
            <publisher>
                <publisherName>Uppsala Läroverk</publisherName>
                <city>Uppsala</city>
            </publisher>
        </publication>
    """)

    agent = create_origin_info(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        agent,
        """
        <originInfo>
            <name type="corporate" otherType="publisher" repeatId="0">
                <namePart type="publisher">Uppsala Läroverk</namePart>
                <place>
                    <placeTerm>Uppsala</placeTerm>
                </place>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </name>
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

    source_record = ET.fromstring(f"""
        <publication>
            <publisher>
                <publishingHouse>
                    <publishingHouseId>{mock_old_id}</publishingHouseId>
                </publishingHouse>
                <city>Uppsala</city>
            </publisher>
        </publication>
        """)

    agent = create_origin_info(source_record, mock_context)

    assert_equal_for_xml_and_xml_string(
        agent,
        f""" 
        <originInfo>
            <name type="corporate" otherType="publisher" repeatId="0">
                <publisher>
                    <linkedRecordType>diva-publisher</linkedRecordType>
                    <linkedRecordId>{expected_cora_id}</linkedRecordId>
                </publisher>
                <place>
                    <placeTerm>Uppsala</placeTerm>
                </place>
                <role>
                    <roleTerm>pbl</roleTerm>
                </role>
            </name>
        </originInfo>
        """,
    )


def test_does_not_include_publisher_if_book_chapter():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>58</publicationTypeId>
                <publicationTypeCode>chapter</publicationTypeCode>
            </publicationType>
            <dateIssued>2022</dateIssued>
            <publisher>
                <publisherName>Uppsala Läroverk</publisherName>
                <city>Uppsala</city>
            </publisher>
        </publication>
        """)

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


def test_does_not_include_publisher_if_conference_paper():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeId>58</publicationTypeId>
                <publicationTypeCode>conferencePaper</publicationTypeCode>
            </publicationType>
            <dateIssued>2022</dateIssued>
            <publisher>
                <publisherName>Uppsala Läroverk</publisherName>
                <city>Uppsala</city>
            </publisher>
        </publication>
        """)

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


def test_does_not_include_publisher_if_editorial_letter():
    source_record = ET.fromstring("""
        <publication>
            <publicationType>
                <publicationTypeCode>article</publicationTypeCode>
            </publicationType>
            <subtype>
                <publicationSubtypeCode>letter</publicationSubtypeCode>
            </subtype>
            <dateIssued>2022</dateIssued>
            <publisher>
                <publisherName>Uppsala Läroverk</publisherName>
                <city>Uppsala</city>
            </publisher>
        </publication>
        """)

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
