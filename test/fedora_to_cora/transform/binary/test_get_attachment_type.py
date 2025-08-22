import pytest
from xml.etree import ElementTree as ET
from fedora_to_cora.transform.binary.get_attachment_type import get_attachment_type


@pytest.mark.parametrize(
    "file_label_id,expected_output",
    [
        ("50", "fullText"),
        ("51", "errata"),
        ("52", "references"),
        ("53", "summary"),
        ("54", "inside"),
        ("55", "cover"),
        ("56", "toc"),
        ("57", "popularSummary"),
        ("58", "audio"),
        ("59", "movie"),
        ("60", "imageDiva"),
        ("61", "attachment"),
        ("62", "notificationOfSubmissionOfAThesis"),
        ("63", "software"),
        ("64", "previewImage"),
        ("65", "dataSet"),
    ],
)
def test_get_attachment_type_returns_correct_attachment_type(
    file_label_id, expected_output
):
    source_attachment = ET.fromstring(
        f"""
        <attachment>
            <fileLabel>
                <fileLabelId>{file_label_id}</fileLabelId>
            </fileLabel>
        </attachment>
        """
    )
    assert get_attachment_type(source_attachment) == expected_output


def test_get_attachment_type_returns_none_for_unknown_file_label_id():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                <fileLabelId>unknown</fileLabelId>
            </fileLabel>
        </attachment>
        """
    )
    pytest.raises(ValueError, get_attachment_type, source_attachment)


def test_no_file_label_id_raises_type_error():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <fileLabel>
                
            </fileLabel>
        </attachment>
        """
    )
    pytest.raises(ValueError, get_attachment_type, source_attachment)
