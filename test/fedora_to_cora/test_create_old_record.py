import xml.etree.ElementTree as ET
import pytest
from unittest.mock import MagicMock
from common.test_helper import assert_equal_for_xml_and_xml_string
from common.common_data import read_source_xml
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from fedora_to_cora.migrate_old_record import old_record_migrate, transform_old_record


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
            <id>{pid}</id>
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
    assert cora_record.findtext("./recordXml") == (
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
            <id>{pid}</id>
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
    assert cora_record.findtext("./recordXml") == f"<![CDATA[{expected_source_xml}]]>"


def test_old_record_migrate_returns_success_tuple(monkeypatch):
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordSuccessResult(
            record_id="123", response_data=ET.Element("record")
        ),
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert result == (True, None)


def test_old_record_migrate_returns_failure_tuple(monkeypatch):
    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record",
        lambda *args, **kwargs: CreateRecordFailureResult("create failed"),
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert result == (False, ["create failed"])


def test_old_record_migrate_returns_exception_as_error(monkeypatch):
    def raise_create_error(*args, **kwargs):
        raise RuntimeError("create raised")

    monkeypatch.setattr(
        "fedora_to_cora.migrate_old_record.create_record", raise_create_error
    )

    result = old_record_migrate(
        ET.fromstring("<record><pid>123</pid></record>"), MagicMock()
    )

    assert result == (False, ["create raised"])
