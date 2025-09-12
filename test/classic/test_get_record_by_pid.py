from classic.get_publications_from_fedora import get_publications_from_fedora
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_get_record_by_pid(requests_mock):
    pid = "some-pid"
    requests_mock.get(
        f"https://uu.diva-portal.org:8443/fedora/get/{pid}/MODEL_NOREF",
        text="<record></record>",
    )
    result = get_publications_from_fedora(pid)
    assert_equal_for_xml_and_xml_string(result, "<record></record>")
