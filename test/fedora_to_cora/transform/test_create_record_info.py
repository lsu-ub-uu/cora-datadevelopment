from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_record_info import create_record_info
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_record_info():
    source_record = ET.fromstring(
        """
    <publication>
        <publicationType>
            <publicationTypeId>50</publicationTypeId>
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
    </publication>
    """
    )

    record_info = create_record_info(source_record)

    assert_equal_for_xml_and_xml_string(
        record_info,
        """
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
        </recordInfo>
        """,
    )
