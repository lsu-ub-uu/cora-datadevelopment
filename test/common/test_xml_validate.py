import xml.etree.ElementTree as ET
import pytest
from common.xml_validate import XMLSpec, XMLValidationError, validate_xml


def test_validate_xml_raises_error_on_unknown_child():
    spec: XMLSpec = {"known1": "text", "known2": "text"}

    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <unknown>value2</unknown>
            </source>
        """
    )

    with pytest.raises(
        XMLValidationError, match="Unknown child element <unknown> found in <source>"
    ):
        validate_xml(source, spec)


def test_validate_xml_does_not_raise_when_child_missing():
    spec: XMLSpec = {"known1": "text", "known2": "text"}

    source = ET.fromstring(
        """
            <source>
                <known1></known1>
            </source>
        """
    )

    validate_xml(source, spec)


def test_validate_xml_raises_error_when_expecting_text_and_got_element():
    spec: XMLSpec = {"known1": "text", "known2": "text"}

    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>
                    <unknown></unknown>
                </known2>
            </source>
            """
    )

    with pytest.raises(
        XMLValidationError,
        match="Expected text content in <known2>, but found child elements",
    ):
        validate_xml(source, spec)


def test_validate_xml_raises_error_when_expecting_element_and_got_text():
    spec: XMLSpec = {
        "known1": "text",
        "known2": {"known2.1": "text", "known2.2": "text"},
    }
    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>some text instead of elements</known2>
            </source>
            """
    )

    with pytest.raises(
        XMLValidationError,
        match="Expected child elements in <known2>, but found text content",
    ):
        validate_xml(source, spec)


def test_validate_xml_does_not_raise_error_when_expecting_element_and_got_empty_tag():
    spec: XMLSpec = {
        "known1": "text",
        "known2": {"known2.1": "text", "known2.2": "text"},
    }
    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2></known2>
            </source>
            """
    )

    validate_xml(source, spec)


def test_validate_xml_raises_error_when_child_has_unknown_element():
    spec: XMLSpec = {
        "known1": "text",
        "known2": {"known2.1": "text", "known2.2": "text"},
    }

    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>
                    <known2.1></known2.1>
                    <unknown></unknown>
                </known2>
            </source>
            """
    )

    with pytest.raises(
        XMLValidationError, match="Unknown child element <unknown> found in <known2>"
    ):
        validate_xml(source, spec)


def test_validate_xml_does_not_raise_error_when_child_is_missing_element():
    spec: XMLSpec = {
        "known1": "text",
        "known2": {"known2.1": "text", "known2.2": "text"},
    }

    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>
                    <known2.1></known2.1>
                </known2>
            </source>
            """
    )

    validate_xml(source, spec)
