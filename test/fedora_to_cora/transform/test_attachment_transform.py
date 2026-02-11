from unittest.mock import MagicMock
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.attachment_transform import attachment_transform
import pytest


def test_attachment_transform():
    source_attachment = ET.fromstring(
        """
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
            </attachment>
        """
    )
    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>unpublished</requestedVisibility>
        </attachment>
        """,
    )


def test_label():
    source_attachment = ET.fromstring(
        """
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
            </attachment>
        """
    )
    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>unpublished</requestedVisibility>
        </attachment>
        """,
    )


@pytest.mark.parametrize(
    "validation_type,should_have_attachment_version",
    [
        ("intellectual-property_patent", False),
        ("publication_encyclopedia-entry", False),
        ("conference_proceeding", True),
        ("conference_poster", True),
        ("publication_edited-book", False),
        ("publication_licentiate-thesis-compilation", False),
        ("publication_journal-issue", False),
        ("artistic-work_artistic-thesis", False),
        ("conference_paper", False),
        ("publication_critical-edition", False),
        ("conference_other", True),
        ("publication_report", False),
        ("publication_preprint", False),
        ("publication_book-chapter", True),
        ("publication_book", True),
        ("diva_dissertation", False),
        ("publication_licentiate-thesis-monograph", False),
        ("publication_other", False),
        ("artistic-work_original-creative-work", False),
        ("publication_working-paper", False),
        ("publication_report-chapter", False),
        ("diva_degree-project", False),
        ("publication_foreword-afterword", False),
        ("publication_doctoral-thesis-monograph", False),
        ("publication_doctoral-thesis-compilation", False),
        ("publication_newspaper-article", True),
        ("publication_book-review", True),
        ("publication_magazine-article", True),
        ("publication_journal-article", True),
        ("publication_review-article", True),
        ("publication_editorial-letter", True),
    ],
)
def test_includes_attachment_version_depending_on_validation_type(
    validation_type, should_have_attachment_version
):
    source_attachment = ET.fromstring(
        f"""
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
                <prePrint>true</prePrint>
                <availableFrom>2020-01-01T00:00:00+00:00</availableFrom>
            </attachment>
        """
    )

    attachment = attachment_transform(
        source_attachment,
        validation_type=validation_type,
        binary_record_id="binary:12345",
    )

    if should_have_attachment_version:
        assert attachment.findtext("./note[@type='attachmentVersion']") is not None
    else:
        assert attachment.findtext("./note[@type='attachmentVersion']") is None


@pytest.mark.parametrize(
    "tagName,expected_attachment_version",
    [
        ("prePrint", "submitted"),
        ("postPrint", "accepted"),
        ("print", "published"),
    ],
)
def test_attachment_version_submitted_when_preprint(
    tagName, expected_attachment_version
):
    source_attachment = ET.fromstring(
        f"""
            <attachment>
                <fileLabel>
                    <fileLabelId>50</fileLabelId>
                </fileLabel>
                <path>test.pdf</path>
                <availableFrom>2020-01-01T00:00:00+00:00</availableFrom>
                <{tagName}>true</{tagName}>
            </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_newspaper-article",
        binary_record_id=binary_record_id,
    )

    attachment_version = attachment.findtext("note[@type='attachmentVersion']")
    assert attachment_version == expected_attachment_version


def test_raises_error_when_multiple_attachment_versions():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <prePrint>true</prePrint>
            <postPrint>true</postPrint>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    with pytest.raises(ValueError, match="Multiple attachment versions found"):
        attachment_transform(
            source_attachment,
            validation_type="publication_newspaper-article",
            binary_record_id=binary_record_id,
        )


def test_secrecy():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert attachment.findtext("./adminInfo/secrecy") == "true"


def test_registration_number():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <registrationNumber>1234</registrationNumber>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert (
        attachment.findtext("./adminInfo/identifier[@type='registrationNumber']")
        == "1234"
    )


def test_note_type_attachment():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <path>test.pdf</path>
            <note>Some note about the attachment</note>
            <availableFrom>2020-01-01T00:00:00+00:00</availableFrom>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
        file_upload_message="Some note about the attachment",
    )

    assert (
        attachment.findtext("./adminInfo/note[@type='attachment']")
        == """**The following note was migrated from a DiVA Classic file upload message, and may not refer to this attachment**:\n\nSome note about the attachment"""
    )


def test_display_label():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <selectedFileName>test.pdf</selectedFileName>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <displayLabel>test.pdf</displayLabel>
            <requestedVisibility>unpublished</requestedVisibility>
        </attachment>                                             
    """,
    )


def test_digitized():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <digitized>true</digitized>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>unpublished</requestedVisibility>
            <digitized>true</digitized>
        </attachment>                                             
    """,
    )


def test_print_ready_file():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <printOnDemand>true</printOnDemand>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>unpublished</requestedVisibility>
            <printReadyFile>true</printReadyFile>
        </attachment>                                             
    """,
    )


def test_date_to_be_published():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <availableFrom>2020-01-01T00:00:00+00:00</availableFrom>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>published</requestedVisibility>
            <dateToBePublished>
                <year>2020</year>
                <month>01</month>
                <day>01</day>
            </dateToBePublished>
        </attachment>                                             
    """,
    )


def test_date_to_be_unpublished():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
            </fileLabel>
            <availableUntil>2020-01-01T00:00:00+00:00</availableUntil>
        </attachment>
        """
    )

    binary_record_id = "binary:12345"

    attachment = attachment_transform(
        source_attachment,
        validation_type="publication_report",
        binary_record_id=binary_record_id,
    )

    assert_equal_for_xml_and_xml_string(
        attachment,
        """
        <attachment repeatId="binary:12345">
            <file>
              <linkedRecordType>binary</linkedRecordType>
              <linkedRecordId>binary:12345</linkedRecordId>
            </file>
            <label>fullText</label>
            <requestedVisibility>unpublished</requestedVisibility>
            <dateToBeUnpublished>
                <year>2020</year>
                <month>01</month>
                <day>01</day>
            </dateToBeUnpublished>
        </attachment>                                             
    """,
    )
