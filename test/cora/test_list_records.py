import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.list_records import list_records


def test_list_records_returns_list_of_et_elements(requests_mock):

    context = MockContext("https://someurl.com/rest/", "someToken")

    requests_mock.get(
        f"https://someurl.com/rest/metadata",
        text="""
        <dataList>
            <data>
                <record><id>record1</id></record>
                <record><id>record2</id></record>
            </data>
        </dataList>
        """,
    )

    records = list_records(context, "metadata")
    assert len(records) == 2
    assert_equal_for_xml_and_xml_string(records[0], "<record><id>record1</id></record>")
    assert_equal_for_xml_and_xml_string(records[1], "<record><id>record2</id></record>")


def test_list_records_raises_exception_on_http_error(requests_mock):
    context = MockContext("https://someurl.com/rest/", "someToken")

    requests_mock.get(
        f"https://someurl.com/rest/metadata",
        status_code=500,
        text="Internal Server Error",
    )

    try:
        list_records(context, "metadata")
        assert False, "Expected an exception to be raised"
    except Exception as e:
        assert (
            str(e)
            == "500 Server Error: None for url: https://someurl.com/rest/metadata"
        )
