import xml.etree.ElementTree as ET
from fedora_to_cora.transform.transform_output_to_classic_quality import (
    transform_output_to_classic_quality,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_adds_internal_note_with_validation_errors():
    cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2>someValue3</someChild2>
        </record>
        """
    )
    validation_errors = [
        "Missing required field",
        "Invalid format",
    ]
    classic_quality_output = transform_output_to_classic_quality(
        cora_output, validation_errors
    )
    assert_equal_for_xml_and_xml_string(
        classic_quality_output,
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2>someValue3</someChild2>
            <adminInfo>
                <note type="internal">Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )


def test_adds_validation_errors_to_existing_internal_note():
    cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>2026</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2>someValue3</someChild2>
            <adminInfo>
                <note type="internal">Some internal note.</note>
            </adminInfo>
        </record>
        """
    )
    validation_errors = [
        "Missing required field",
        "Invalid format",
    ]
    classic_quality_output = transform_output_to_classic_quality(
        cora_output, validation_errors
    )
    assert_equal_for_xml_and_xml_string(
        classic_quality_output,
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
            </recordInfo>
            <dataQuality>classic</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2>someValue3</someChild2>
            <adminInfo>
                <note type="internal">Some internal note.Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic. Validation errors:- Missing required field- Invalid format</note>
            </adminInfo>
        </record>
        """,
    )
