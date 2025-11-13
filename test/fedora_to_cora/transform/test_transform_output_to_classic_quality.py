import xml.etree.ElementTree as ET
from fedora_to_cora.transform.transform_output_to_classic_quality import (
    transform_output_to_classic_quality,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_adds_repeat_id_to_children():
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
            <someChild1>someValue1</someChild1>
            <someChild2>someValue2</someChild2>
            <someChild3>someValue3</someChild3>
        </record>
        """
    )

    classic_quality_output = transform_output_to_classic_quality(cora_output, [])

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
            <dataQuality repeatId="1">classic</dataQuality>
            <someChild1 repeatId="2">someValue1</someChild1>
            <someChild2 repeatId="3">someValue2</someChild2>
            <someChild3 repeatId="4">someValue3</someChild3>
        </record>
        """,
    )


def test_adds_repeat_id_to_nested_children():
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
            <someChild1>
                <someGrandChild1>someValue1.1</someGrandChild1>
                <someGrandChild2>someValue1.2</someGrandChild2>
            </someChild1>
            <someChild2>someValue2</someChild2>
        </record>
        """
    )

    classic_quality_output = transform_output_to_classic_quality(cora_output, [])

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
            <dataQuality repeatId="1">classic</dataQuality>
            <someChild1 repeatId="2">
                <someGrandChild1 repeatId="0">someValue1.1</someGrandChild1>
                <someGrandChild2 repeatId="1">someValue1.2</someGrandChild2>
            </someChild1>
            <someChild2 repeatId="3">someValue2</someChild2>
        </record>
        """,
    )


def test_does_not_addrepeat_id_to_record_info_children():
    cora_output = ET.fromstring(
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>publication_report</linkedRecordId>
                </validationType>
                 <someChild1>
                    <someGrandChild1>someValue1.1</someGrandChild1>
                    <someGrandChild2>someValue1.2</someGrandChild2>
                </someChild1>
                <someChild2>someValue2</someChild2>
            </recordInfo>
            <dataQuality>2026</dataQuality>
        </record>
        """
    )

    classic_quality_output = transform_output_to_classic_quality(cora_output, [])

    assert_equal_for_xml_and_xml_string(
        classic_quality_output,
        """
        <record>
            <recordInfo>
                <validationType>
                    <linkedRecordType>validationType</linkedRecordType>
                    <linkedRecordId>classic_publication_report</linkedRecordId>
                </validationType>
                <someChild1>
                    <someGrandChild1>someValue1.1</someGrandChild1>
                    <someGrandChild2>someValue1.2</someGrandChild2>
                </someChild1>
                <someChild2>someValue2</someChild2>
            </recordInfo>
            <dataQuality repeatId="1">classic</dataQuality>
        </record>
        """,
    )


def test_does_not_overwrite_existing_repeat_id():
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

    classic_quality_output = transform_output_to_classic_quality(cora_output, [])

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
            <dataQuality repeatId="1">classic</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2 repeatId="4">someValue3</someChild2>
        </record>
        """,
    )


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
            <dataQuality repeatId="1">classic</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2 repeatId="4">someValue3</someChild2>
            <note type="internal" repeatId="5">Record created with dataQuality "classic" due to validation errors during migration from DiVA Classic.\n\nValidation errors:\n- Missing required field\n- Invalid format</note>
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
            <note type="internal" repeatId="5">Some internal note.</note>
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
            <dataQuality repeatId="1">classic</dataQuality>
            <someChild1 repeatId="one">someValue1</someChild1>
            <someChild1 repeatId="two">someValue2</someChild1>
            <someChild2 repeatId="4">someValue3</someChild2>
            <note type="internal" repeatId="5">Some internal note.\n\nRecord created with dataQuality "classic" due to validation errors during migration from DiVA Classic.\n\nValidation errors:\n- Missing required field\n- Invalid format</note>
        </record>
        """,
    )
