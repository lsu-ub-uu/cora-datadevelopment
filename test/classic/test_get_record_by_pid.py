import re

from classic.get_record_by_pid import get_record_by_pid
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_get_record_by_pid(requests_mock):
    pid = "some-pid"
    requests_mock.get(re.compile(
        f"https?://[^/]+/fedora/get/{pid}/MODEL_NOREF"),
        text="<record></record>",
    )
    result = get_record_by_pid(pid)
    assert_equal_for_xml_and_xml_string(result, "<record></record>")
