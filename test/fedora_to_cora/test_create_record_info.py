from xml.etree import ElementTree as ET
from fedora_to_cora.create_record_info import create_record_info

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


def test_create_record_info_sets_validation_type():
    record_info = create_record_info(source_record)
    validation_type = record_info.find(".//validationType")
    assert (
        validation_type is not None
        and validation_type.text == "publication_journal-article"
    )


def test_create_record_info_sets_data_divider():
    record_info = create_record_info(source_record)
    validation_type = record_info.find(".//dataDivider")
    assert validation_type is not None and validation_type.text == "divaData"


def test_create_record_info_sets_permission_unit():
    record_info = create_record_info(source_record)

    linked_record_type = record_info.find(".//permissionUnit/linkedRecordType")
    assert (
        linked_record_type is not None and linked_record_type.text == "permissionUnit"
    )

    linked_record_id = record_info.find(".//permissionUnit/linkedRecordId")
    assert linked_record_id is not None and linked_record_id.text == "kth"


def test_create_record_info_sets_visibility():
    record_info = create_record_info(source_record)
    visibility = record_info.find("visibility")
    assert visibility is not None and visibility.text == "published"


def test_create_record_info_sets_oldId():
    record_info = create_record_info(source_record)
    old_id = record_info.find("oldId")
    assert old_id is not None and old_id.text == "456"
