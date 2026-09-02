from unittest.mock import MagicMock, patch

import pytest

from classic.get_pids_for_domain import get_pids_for_domain

SOLR_URL = "http://localhost:8080/solr-admin/dream/select"


def test_get_pids_for_domain(requests_mock):
    requests_mock.get(
        f"{SOLR_URL}?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="2"></result></response>',
    )

    requests_mock.get(
        f"{SOLR_URL}?q=*%3A*&fq=domain%3Atest_domain&rows=2&fl=PID&wt=xml&indent=true",
        text='<response><result><doc><str name="PID">pid1</str></doc><doc><str name="PID">pid2</str></doc></result></response>',
    )

    pids = get_pids_for_domain("test_domain", solr_url=SOLR_URL)

    assert pids == ["pid1", "pid2"]


def test_get_pids_for_domain_no_results(requests_mock):
    requests_mock.get(
        f"{SOLR_URL}?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="0"></result></response>',
    )

    requests_mock.get(
        f"{SOLR_URL}?q=*%3A*&fq=domain%3Atest_domain&rows=0&fl=PID&wt=xml&indent=true",
        text="<response><result></result></response>",
    )

    pids = get_pids_for_domain("test_domain", solr_url=SOLR_URL)

    assert pids == []


def test_filters_out_drafts(requests_mock):
    requests_mock.get(
        f"{SOLR_URL}?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="3"></result></response>',
    )

    requests_mock.get(
        f"{SOLR_URL}?q=*%3A*&fq=domain%3Atest_domain&rows=3&fl=PID&wt=xml&indent=true",
        text='<response><result><doc><str name="PID">diva2:1234</str></doc><doc><str name="PID">diva2-draft:4321</str></doc><doc><str name="PID">diva2:5432</str></doc></result></response>',
    )

    pids = get_pids_for_domain("test_domain", solr_url=SOLR_URL)

    assert pids == ["diva2:1234", "diva2:5432"]


def test_get_pids_for_domain_num_found_request_fail(requests_mock):
    requests_mock.get(
        f"{SOLR_URL}?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception, match="500") as exc_info:
        get_pids_for_domain("test_domain", solr_url=SOLR_URL)
        assert "500" in str(exc_info.value)


def test_get_pids_for_domain_get_pids_fail(requests_mock):
    requests_mock.get(
        f"{SOLR_URL}?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="0"></result></response>',
    )

    requests_mock.get(
        f"{SOLR_URL}?q=*%3A*&fq=domain%3Atest_domain&rows=0&fl=PID&wt=xml&indent=true",
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception) as exc_info:
        get_pids_for_domain("test_domain", solr_url=SOLR_URL)
        assert "500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)
