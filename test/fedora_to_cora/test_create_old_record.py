import xml.etree.ElementTree as ET
import pytest
from unittest.mock import MagicMock
from common.test_helper import assert_equal_for_xml_and_xml_string
from common.common_data import read_source_xml
from common.xml_utils import pretty_print_xml
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from fedora_to_cora.migrate_old_record import (
    old_record_migrate,
    transform_old_record,
    update_record_info_with_old_record_link,
)


def test_create_old_record():
    pid = "12345"
    source_record = f"""<record>
    <pid>{pid}</pid>
    <publicationType>
        <publicationTypeCode>journal</publicationTypeCode>
    </publicationType>
</record>"""

    cora_record = transform_old_record(ET.fromstring(source_record))
    assert cora_record.tag == "oldRecord"
    assert_equal_for_xml_and_xml_string(
        cora_record.find("./recordInfo"),
        f"""
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-oldRecord</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>{pid}</oldId>
        </recordInfo>""",
    )
    assert cora_record.findtext("./record") == (
        f"<![CDATA[<record>   <pid>{pid}</pid>   <publicationType> "
        "    <publicationTypeCode>journal</publicationTypeCode>   "
        "</publicationType> </record>]]>"
    )


def test_create_full_publication_old_record():
    source_record = read_source_xml("data/fedora/testData/publication.xml")
    pid = source_record.findtext("./pid")

    cora_record = transform_old_record(source_record)

    assert cora_record.tag == "oldRecord"
    assert_equal_for_xml_and_xml_string(
        cora_record.find("./recordInfo"),
        f"""
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-oldRecord</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>{pid}</oldId>
        </recordInfo>""",
    )

    ET.indent(source_record)
    expected_source_xml = ET.tostring(source_record, encoding="unicode")
    expected_source_xml = expected_source_xml.replace("\n", " ").strip()
    assert cora_record.findtext("./record") == f"<![CDATA[{expected_source_xml}]]>"


def test_old_record_migrate_returns_created_result(monkeypatch):
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordSuccessResult(
            record_id="123", response_data=ET.Element("record")
        ),
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert (result.status, result.cora_old_record_id, result.error) == (
        "CREATED",
        "123",
        None,
    )


def test_old_record_migrate_returns_failed_result(monkeypatch):
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordFailureResult("create failed"),
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert (result.status, result.cora_old_record_id, result.error) == (
        "FAILED",
        None,
        "create failed",
    )


def test_old_record_migrate_returns_exception_as_error(monkeypatch):
    def raise_create_error(*args, **kwargs):
        raise RuntimeError("create raised")

    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record", raise_create_error
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert (result.status, result.cora_old_record_id, result.error) == (
        "FAILED",
        None,
        "create raised",
    )


@pytest.mark.parametrize(
    "pid, expected_status", [("123", "SKIPPED"), ("456", "FAILED")]
)
def test_old_record_migrate_checks_duplicate_for_source_pid(
    monkeypatch, pid, expected_status
):
    error = "A record matching the unique rule with [key: oldId, value: 123] already exists in the system"
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordFailureResult(error, status=409),
    )

    result = old_record_migrate(
        ET.fromstring(f"<record><pid>{pid}</pid></record>"), MagicMock()
    )

    assert result.status == expected_status
    assert result.cora_old_record_id is None
    assert result.error is not None


def test_old_record_migrate_failure_without_error(monkeypatch):
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordFailureResult(None),
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert result.status == "FAILED"
    assert result.error is None


def test_update_record_info():
    pid = "some_test_pid"
    record = ET.fromstring("""
        <output>
            <recordInfo>
                <id>some_id</id>
                <type>
                    <linkedRecordType>recordType</linkedRecordType>
                    <linkedRecordId>diva-output</linkedRecordId>
                </type>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>diva-output</linkedRecordId>
                </validationType>
            </recordInfo>
        </output>""")

    update_record_info_with_old_record_link(pid, record)
    assert_equal_for_xml_and_xml_string(
        record,
        pretty_print_xml(ET.fromstring(f"""<output>
                        <recordInfo>
                            <id>some_id</id>
                            <type>
                                <linkedRecordType>recordType</linkedRecordType>
                                <linkedRecordId>diva-output</linkedRecordId>
                            </type>
                            <validationType>
                                <linkedRecordType>validationType</linkedRecordType>
                                <linkedRecordId>diva-output</linkedRecordId>
                            </validationType>
                            <oldRecord>
                                <linkedRecordType>diva-oldRecord</linkedRecordType>
                                <linkedRecordId>{pid}</linkedRecordId>
                            </oldRecord>
                        </recordInfo>
                    </output>""")),
    )


@pytest.mark.parametrize(
    ("cora_old_record_id", "output", "error_message"),
    [
        ("old-record-id", None, "record should not be None"),
        (None, ET.Element("output"), "pid should not be None"),
        ("old-record-id", ET.Element("output"), "recordInfo should not be None"),
    ],
)
def test_update_record_info_rejects_missing_required_values(
    cora_old_record_id, output, error_message
):
    with pytest.raises(AssertionError, match=error_message):
        update_record_info_with_old_record_link(cora_old_record_id, output)
