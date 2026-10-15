from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_record_info import create_record_info
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from unittest.mock import Mock
import pytest


@pytest.mark.parametrize("old_record_id", ["old-record:456", "diva-oldRecord not found for old ID: 456"])
def test_create_record_info(monkeypatch, old_record_id):
    context = MockContext()
    lookup = Mock(return_value=old_record_id)
    monkeypatch.setattr(
        "fedora_to_cora.transform.create_record_info.get_cora_id_by_old_id", lookup
    )
    source_record = ET.fromstring(
        """
    <publication>
        <publicationType>
            <publicationTypeId>50</publicationTypeId>
            <publicationTypeCode>article</publicationTypeCode>
        </publicationType>
        <administrativeInfo>
            <domain>kth</domain>
            <updaters>
                <userInformation>
                    <userAction>AUTOPUBLISHED</userAction>
                </userInformation>
            </updaters>
        </administrativeInfo>
        <pid>456</pid>
        <nbn>urn:nbn:se:nordiskamuseet:some-nbn</nbn>
    </publication>
    """
    )

    record_info = create_record_info(source_record, context)
    lookup.assert_called_once_with("456", record_type="diva-oldRecord", context=context)

    assert_equal_for_xml_and_xml_string(
        record_info,
        f"""
        <recordInfo>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>publication_journal-article</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <permissionUnit>
                <linkedRecordType>permissionUnit</linkedRecordType>
                <linkedRecordId>kth</linkedRecordId>           
            </permissionUnit>
            <visibility>published</visibility>
            <oldId>456</oldId>
            <urn>urn:nbn:se:nordiskamuseet:some-nbn</urn>
            <oldRecord>
                <linkedRecordType>diva-oldRecord</linkedRecordType>
                <linkedRecordId>{old_record_id}</linkedRecordId>
            </oldRecord>
        </recordInfo>
        """,
    )
