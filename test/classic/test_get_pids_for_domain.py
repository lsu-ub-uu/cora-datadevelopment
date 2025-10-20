from unittest.mock import MagicMock, patch

import pytest

from classic.get_pids_for_domain import get_pids_for_domain


def test_get_pids_for_domain(monkeypatch, requests_mock):
    monkeypatch.setattr("classic.get_pids_for_domain.SSHTunnel", MagicMock())

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="2"></result></response>',
    )

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=*%3A*&fq=domain%3Atest_domain&rows=2&fl=PID&wt=xml&indent=true",
        text='<response><result><doc><str name="PID">pid1</str></doc><doc><str name="PID">pid2</str></doc></result></response>',
    )

    pids = get_pids_for_domain("test_domain")

    assert pids == ["pid1", "pid2"]


def test_get_pids_for_domain_no_results(monkeypatch, requests_mock):
    monkeypatch.setattr("classic.get_pids_for_domain.SSHTunnel", MagicMock())

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="0"></result></response>',
    )

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=*%3A*&fq=domain%3Atest_domain&rows=0&fl=PID&wt=xml&indent=true",
        text="<response><result></result></response>",
    )

    pids = get_pids_for_domain("test_domain")

    assert pids == []


def test_filters_out_drafts(monkeypatch, requests_mock):
    monkeypatch.setattr("classic.get_pids_for_domain.SSHTunnel", MagicMock())

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        text='<response><result numFound="3"></result></response>',
    )

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=*%3A*&fq=domain%3Atest_domain&rows=3&fl=PID&wt=xml&indent=true",
        text='<response><result><doc><str name="PID">diva2:1234</str></doc><doc><str name="PID">diva2-draft:4321</str></doc><doc><str name="PID">diva2:5432</str></doc></result></response>',
    )

    pids = get_pids_for_domain("test_domain")

    assert pids == ["diva2:1234", "diva2:5432"]


def test_get_pids_for_domain_num_found_request_fail(monkeypatch, requests_mock):
    monkeypatch.setattr("classic.get_pids_for_domain.SSHTunnel", MagicMock())

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=domain%3Atest_domain&start=0&rows=0&wt=xml&indent=true",
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception) as exc_info:
        get_pids_for_domain("test_domain")
        assert "500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)


def test_get_pids_for_domain_get_pids_fail(monkeypatch, requests_mock):
    monkeypatch.setattr("classic.get_pids_for_domain.SSHTunnel", MagicMock())

    requests_mock.get(
        "http://localhost:8080/solr-admin/dream/select?q=*%3A*&fq=domain%3Atest_domain&rows=0&fl=PID&wt=xml&indent=true",
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception) as exc_info:
        get_pids_for_domain("test_domain")
        assert "500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)
