from freezegun import freeze_time
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.create import CreateRecordFailureResult, CreateRecordSuccessResult
from cora.update import UpdateRecordResult
from cora.upload import UploadError
from fedora_to_cora.attachments_migrate import attachments_migrate
from cora.context import MockContext


def test_attachments_migrate(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
        <publicationType>
            <publicationTypeCode>report</publicationTypeCode>
        </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    
                    <fileName>test.pdf</fileName>
                </attachment>
                 <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test2.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert binary_record_transform_mock.call_count == 2
    assert create_record_mock.call_count == 2
    assert migrate_binary_mock.call_count == 2
    assert attachments_transform_mock.call_count == 2
    assert update_record_mock.call_count == 1

    assert len(update_record_mock.mock_calls) == 1
    updated_cora_record = update_record_mock.mock_calls[0].args[0]
    assert_equal_for_xml_and_xml_string(
        updated_cora_record,
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                    <attachments>
                        <reviewed>true</reviewed>
                        <attachment repeatId="test.pdf">
                            <attachmentFile>
                                <linkedRecordType>binary</linkedRecordType>
                                <linkedRecordId>binary:12345</linkedRecordId>
                            </attachmentFile>
                            <type>fullText</type>
                            <adminInfo>
                                <availability>availableNow</availability>
                            </adminInfo>
                        </attachment>
                        <attachment repeatId="test2.pdf">
                            <attachmentFile>
                                <linkedRecordType>binary</linkedRecordType>
                                <linkedRecordId>binary:12345</linkedRecordId>
                            </attachmentFile>
                            <type>fullText</type>
                            <adminInfo>
                                <availability>availableNow</availability>
                            </adminInfo>
                        </attachment>
                    </attachments>
                </output>
            </data>
        </record>
        """,
    )


def test_failed_to_create_binary_record(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch, fail=True)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <pid>pid:123</pid>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert migrate_binary_mock.call_count == 0
    assert attachments_transform_mock.call_count == 0
    assert update_record_mock.call_count == 0

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "Failed to create binary record"


def test_failed_to_migrate_binary(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch, fail=True)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)
    delete_record_mock = _set_up_delete_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <pid>pid:123</pid>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert migrate_binary_mock.call_count == 1
    assert attachments_transform_mock.call_count == 0
    assert update_record_mock.call_count == 0
    assert delete_record_mock.call_count == 1

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "Failed to migrate binary"


def test_failed_to_update_record(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch, fail=True)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)
    delete_record_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.delete_record", delete_record_mock
    )

    source_record = ET.fromstring(
        """
        <publication>
            <pid>pid:123</pid>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert binary_record_transform_mock.call_count == 1
    assert create_record_mock.call_count == 1
    assert migrate_binary_mock.call_count == 1
    assert attachments_transform_mock.call_count == 1
    assert update_record_mock.call_count == 1
    assert delete_record_mock.call_count == 1

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "Failed to update record"


def test_roll_back_binary_records_when_something_fails(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch)
    migrate_binary_mock.side_effect = [None, UploadError("Failed to upload binary")]

    update_record_mock = _set_up_update_record_mock(monkeypatch)

    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    delete_record_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.delete_record", delete_record_mock
    )

    source_record = ET.fromstring(
        """
        <publication>
            <pid>pid:123</pid>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test.pdf</fileName>
                </attachment>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test2.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    success, errors = attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert binary_record_transform_mock.call_count == 2
    assert create_record_mock.call_count == 2
    assert migrate_binary_mock.call_count == 2
    assert attachments_transform_mock.call_count == 1
    assert update_record_mock.call_count == 0
    assert delete_record_mock.call_count == 2

    assert not success
    assert errors is not None
    assert len(errors) == 1
    assert errors[0] == "UploadError: Failed to upload binary"


def test_file_upload_message(monkeypatch):
    _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    _set_up_update_record_mock(monkeypatch)
    _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <pid>pid:123</pid>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <administrativeInfo>
                <fileUploadMessage>Some note about the attachment</fileUploadMessage>
            </administrativeInfo>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test.pdf</fileName>
                </attachment>
                 <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test2.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    assert (
        attachments_transform_mock.mock_calls[0].kwargs["file_upload_message"]
        == "Some note about the attachment"
    )
    assert (
        attachments_transform_mock.mock_calls[1].kwargs["file_upload_message"]
        == "Some note about the attachment"
    )


def test_respects_attachment_order(monkeypatch):
    _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    _set_up_binary_record_transform_mock(monkeypatch)
    _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
        <publicationType>
            <publicationTypeCode>report</publicationTypeCode>
        </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <reviewed>false</reviewed>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                </attachment>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>3</order>
                    <fileName>test2.pdf</fileName>
                </attachment>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>1</order>
                    <fileName>test3.pdf</fileName>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    updated_cora_record = update_record_mock.mock_calls[0].args[0]
    assert_equal_for_xml_and_xml_string(
        updated_cora_record,
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                    <attachments>
                        <reviewed>true</reviewed>
                        <attachment repeatId="test3.pdf">
                            <attachmentFile>
                                <linkedRecordType>binary</linkedRecordType>
                                <linkedRecordId>binary:12345</linkedRecordId>
                            </attachmentFile>
                            <type>fullText</type>
                            <adminInfo>
                                <availability>availableNow</availability>
                            </adminInfo>
                        </attachment>
                        <attachment repeatId="test1.pdf">
                            <attachmentFile>
                                <linkedRecordType>binary</linkedRecordType>
                                <linkedRecordId>binary:12345</linkedRecordId>
                            </attachmentFile>
                            <type>fullText</type>
                            <adminInfo>
                                <availability>availableNow</availability>
                            </adminInfo>
                        </attachment>
                        <attachment repeatId="test2.pdf">
                            <attachmentFile>
                                <linkedRecordType>binary</linkedRecordType>
                                <linkedRecordId>binary:12345</linkedRecordId>
                            </attachmentFile>
                            <type>fullText</type>
                            <adminInfo>
                                <availability>availableNow</availability>
                            </adminInfo>
                        </attachment>
                    </attachments>
                </output>
            </data>
        </record>
        """,
    )


def test_attachments_note(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_binary_mock = _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)
    binary_record_transform_mock = _set_up_binary_record_transform_mock(monkeypatch)
    attachments_transform_mock = _set_up_attachments_transform_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    
                    <fileName>test.pdf</fileName>
                </attachment>
                <attachment>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <fileName>test2.pdf</fileName>
                </attachment>
            </attachments>
            <administrativeInfo>
                <fileUploadMessage>Some note about the attachments</fileUploadMessage>
            </administrativeInfo>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(
        source_record,
        cora_record,
        MockContext(),
    )

    updated_cora_record = update_record_mock.mock_calls[0].args[0]

    assert (
        updated_cora_record.findtext("./data/output/attachments/note")
        == "Some note about the attachments"
    )


# 1.1
def test_migrate_attachment_waiting_to_be_published(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>true</toBePublished>
                    <toBeArchived>false</toBeArchived>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_unpublished is None
    assert actual_date_to_be_published is None


# 1.2
@freeze_time("2023-01-02T12:00:00+00:00")
def test_migrate_attachment_published(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "published"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_published is None
    assert actual_date_to_be_unpublished is None


# 2.1
@freeze_time("2023-01-02T12:00:00+00:00")
def test_migrate_attachment_future_publish_date(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <tempAvailableFrom>2023-01-03T12:00:00+00:00</tempAvailableFrom>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "published" == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_published,
        """
       <dateToBePublished>
            <year>2023</year>
            <month>01</month>
            <day>03</day>
        </dateToBePublished>                                 
    """,
    )
    assert actual_date_to_be_unpublished is None


# 2.2
@freeze_time("2023-01-02T12:00:00+00:00")
def test_migrate_attachment_future_publish_date_approved_by_admin(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-03T12:00:00+00:00</availableFrom>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_published,
        """
       <dateToBePublished>
            <year>2023</year>
            <month>01</month>
            <day>03</day>
        </dateToBePublished>                                 
    """,
    )
    assert actual_date_to_be_unpublished is None


# 2.3
@freeze_time("2023-01-02T12:00:00+00:00")
def test_migrate_attachment_future_publish_date_has_passed(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "published"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_published is None
    assert actual_date_to_be_unpublished is None


# 3.1
def test_migrate_attachment_waiting_to_be_archived(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>true</toBeArchived>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "unpublished"
    assert actual_date_to_be_published is None
    assert actual_date_to_be_unpublished is None


# 3.2
@freeze_time("2023-01-02T12:00:00+00:00")
def test_migrate_attachment_archived(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <archiveOnly>true</archiveOnly>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "unpublished"
    assert actual_date_to_be_published is None
    assert actual_date_to_be_unpublished is None


# 4.1
def test_migrate_attachment_waiting_for_future_available_until(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>true</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableUntil>2024-01-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output>
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_published is None
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2024</year>
            <month>01</month>
            <day>01</day>
        </dateToBeUnpublished>                                 
    """,
    )


# 4.2
@freeze_time("2023-02-02T12:00:00+00:00")
def test_migrate_attachment_future_unpublish_date_approved_by_admin(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                    <availableUntil>2023-03-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]
    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "published"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>03</month>
            <day>01</day>
        </dateToBeUnpublished>                                 
    """,
    )
    assert actual_date_to_be_published is None


# 4.3
@freeze_time("2023-03-01T12:00:00+00:00")
def test_migrate_attachment_future_unpublish_date_has_passed(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-01-01T12:00:00+00:00</availableFrom>
                    <availableUntil>2023-02-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>02</month>
            <day>01</day>
        </dateToBeUnpublished>                                 
    """,
    )
    assert actual_date_to_be_published is None


# 5.1
@freeze_time("2023-01-01T12:00:00+00:00")
def test_migrate_attachment_future_wished_publish_and_unpublish(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <tempAvailableFrom>2023-02-02T12:00:00+00:00</tempAvailableFrom>
                    <availableUntil>2023-03-03T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_published,
        """
       <dateToBePublished>
            <year>2023</year>
            <month>02</month>
            <day>02</day>
        </dateToBePublished>                                 
    """,
    )
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>03</month>
            <day>03</day>
        </dateToBeUnpublished>                                 
    """,
    )


# 5.2
@freeze_time("2023-01-01T12:00:00+00:00")
def test_migrate_attachment_future_publish_and_unpublish_approved_by_admin(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-02-01T12:00:00+00:00</availableFrom>
                    <availableUntil>2023-03-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_published,
        """
       <dateToBePublished>
            <year>2023</year>
            <month>02</month>
            <day>01</day>
        </dateToBePublished>                                 
    """,
    )
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>03</month>
            <day>01</day>
        </dateToBeUnpublished>
    """,
    )


# 5.3
@freeze_time("2023-02-02T12:00:00+00:00")
def test_migrate_attachment_past_publish_and_future_unpublish(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-02-01T12:00:00+00:00</availableFrom>
                    <availableUntil>2023-03-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "published"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_published is None
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>03</month>
            <day>01</day>
        </dateToBeUnpublished>
    """,
    )


# 5.4
@freeze_time("2023-04-01T12:00:00+00:00")
def test_migrate_attachment_past_publish_and_unpublish(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <availableFrom>2023-02-01T12:00:00+00:00</availableFrom>
                    <availableUntil>2023-03-01T12:00:00+00:00</availableUntil>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "published"
    assert actual_date_to_be_published is None
    assert_equal_for_xml_and_xml_string(
        actual_date_to_be_unpublished,
        """
       <dateToBeUnpublished>
            <year>2023</year>
            <month>03</month>
            <day>01</day>
        </dateToBeUnpublished>
    """,
    )


def test_secrecy(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>false</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <secrecyInfo>
                        <secrecy>true</secrecy>
                    </secrecyInfo>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "true"
    assert actual_requested_visibility == "confidential"
    assert actual_date_to_be_unpublished is None
    assert actual_date_to_be_published is None


def test_secrecy_with_to_be_published(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <toBePublished>true</toBePublished>
                    <toBeArchived>false</toBeArchived>
                    <secrecyInfo>
                        <secrecy>true</secrecy>
                    </secrecyInfo>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    created_binary_record = create_record_mock.call_args.args[0]
    updated_output_record = update_record_mock.call_args.args[0]

    actual_visibility = created_binary_record.findtext("./recordInfo/visibility")
    actual_reviewed = updated_output_record.findtext(
        "./data/output/attachments/reviewed"
    )
    actual_requested_visibility = updated_output_record.findtext(
        "./data/output/attachments/attachment/requestedVisibility"
    )
    actual_date_to_be_unpublished = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBeUnpublished"
    )
    actual_date_to_be_published = updated_output_record.find(
        "./data/output/attachments/attachment/dateToBePublished"
    )

    assert actual_visibility == "unpublished"
    assert actual_reviewed == "false"
    assert actual_requested_visibility == "confidential"
    assert actual_date_to_be_unpublished is None
    assert actual_date_to_be_published is None


def test_skips_deleted_attachment(monkeypatch):
    create_record_mock = _set_up_create_record_mock(monkeypatch)
    migrate_attachment_mock = _set_up_migrate_binary_mock(monkeypatch)
    update_record_mock = _set_up_update_record_mock(monkeypatch)

    source_record = ET.fromstring(
        """
        <publication>
            <publicationType>
                <publicationTypeCode>report</publicationTypeCode>
            </publicationType>
            <pid>pid:123</pid>
            <attachments>
                <attachment>
                    <fileLabel>
                        <fileLabelId>50</fileLabelId>
                    </fileLabel>
                    <order>2</order>
                    <fileName>test1.pdf</fileName>
                    <deleted>true</deleted>
                </attachment>
            </attachments>
        </publication>
        """
    )

    cora_record = ET.fromstring(
        """
        <record>
            <data>
                <output> 
                    <recordInfo>
                        <id>test-output</id>
                    </recordInfo>
                </output>
            </data>
        </record>
        """
    )

    attachments_migrate(source_record, cora_record, MockContext())

    create_record_mock.assert_not_called()
    migrate_attachment_mock.assert_not_called()
    update_record_mock.assert_not_called()


def _set_up_create_record_mock(monkeypatch, fail=False):
    create_record_mock = MagicMock(
        return_value=(
            CreateRecordSuccessResult(
                record_id="binary:12345", response_data=ET.Element("response")
            )
            if not fail
            else CreateRecordFailureResult(error="Failed to create binary record")
        )
    )
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.create_record", create_record_mock
    )
    return create_record_mock


def _set_up_download_attachment_mock(monkeypatch, fail=False):
    download_attachment_mock = MagicMock()
    if fail:
        download_attachment_mock.side_effect = Exception(
            "Failed to download attachment"
        )
    else:
        download_attachment_mock.return_value = b"binary data"
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.download_attachment",
        download_attachment_mock,
    )
    return download_attachment_mock


def _set_up_upload_binary_mock(monkeypatch, fail=False):
    upload_binary_mock = MagicMock()
    if fail:
        upload_binary_mock.side_effect = UploadError("Failed to upload binary")
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.upload_binary", upload_binary_mock
    )
    return upload_binary_mock


def _set_up_migrate_binary_mock(monkeypatch, fail=False):
    migrate_binary_mock = MagicMock()
    if fail:
        migrate_binary_mock.side_effect = Exception("Failed to migrate binary")
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.migrate_binary", migrate_binary_mock
    )
    return migrate_binary_mock


def _set_up_update_record_mock(monkeypatch, fail=False):
    update_record_mock = MagicMock(
        return_value=UpdateRecordResult(
            success=not fail,
            record_id="test" if not fail else None,
            response_data=ET.Element("data") if not fail else None,
            error="Failed to update record" if fail else None,
        )
    )
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.update_record", update_record_mock
    )
    return update_record_mock


def _set_up_binary_record_transform_mock(monkeypatch):
    binary_record_mock = MagicMock()
    binary_record_transform_mock = MagicMock(return_value=binary_record_mock)
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.binary_record_transform",
        binary_record_transform_mock,
    )
    return binary_record_transform_mock


def _set_up_attachments_transform_mock(monkeypatch):

    def _attachment_transform(
        source_attachment,
        validation_type,
        binary_record_id,
        file_upload_message=None,
    ):
        file_name = source_attachment.findtext("./fileName")
        return ET.fromstring(
            f"""
                <attachment repeatId=\"{file_name}\">
                    <attachmentFile>
                    <linkedRecordType>binary</linkedRecordType>
                    <linkedRecordId>binary:12345</linkedRecordId>
                    </attachmentFile>
                    <type>fullText</type>
                    <adminInfo>
                        <availability>availableNow</availability>
                    </adminInfo>
                </attachment>
            """
        )

    attachment_transform_mock = MagicMock(side_effect=_attachment_transform)
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.attachment_transform",
        attachment_transform_mock,
    )
    return attachment_transform_mock


def _set_up_delete_record_mock(monkeypatch):
    delete_record_mock = MagicMock()
    monkeypatch.setattr(
        "fedora_to_cora.attachments_migrate.delete_record", delete_record_mock
    )
    return delete_record_mock
