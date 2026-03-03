import xml.etree.ElementTree as ET
import pytest
from common.common_data import read_source_xml
from common.xml_validate import XMLSpec, XMLValidationError, validate_xml
from fedora_to_cora import fedora_publication_spec
from fedora_to_cora.fedora_publication_spec import fedora_publication_xml_spec


def test_validate_xml_raises_error_on_unknown_child():
    spec: XMLSpec = {"known1": "$ANY_TEXT$", "known2": "$ANY_TEXT$"}

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
    spec: XMLSpec = {"known1": "$ANY_TEXT$", "known2": "$ANY_TEXT$"}

    source = ET.fromstring(
        """
            <source>
                <known1></known1>
            </source>
        """
    )

    validate_xml(source, spec)


def test_validate_xml_raises_error_when_expecting_text_and_got_element():
    spec: XMLSpec = {"known1": "$ANY_TEXT$", "known2": "$ANY_TEXT$"}

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
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
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
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
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
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
    }

    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>{"child": {"subchild": "$ANY_TEXT$", "ignoredchild": "ignore"}}
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
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
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


def test_validate_xml_does_not_raise_error_for_empty_element():
    spec: XMLSpec = {
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
    }
    source = ET.fromstring("""<source></source>""")

    validate_xml(source, spec)


def test_validate_xml_does_not_raise_error_for_repeating_element():
    spec: XMLSpec = {
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
    }
    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>
                    <known2.1>value2.1</known2.1>
                </known2>
                <known2>
                    <known2.1>value2.1</known2.1>
                </known2>
            </source>
        """
    )

    validate_xml(source, spec)


def test_validate_xml_raises_error_for_repeating_element():
    spec: XMLSpec = {
        "known1": "$ANY_TEXT$",
        "known2": {"known2.1": "$ANY_TEXT$", "known2.2": "$ANY_TEXT$"},
    }
    source = ET.fromstring(
        """
            <source>
                <known1>value1</known1>
                <known2>
                    <known2.1>value2.1</known2.1>
                </known2>
                <known2>
                    <known2.1>value2.1</known2.1>
                    <unknown>value2.2</unknown>
                </known2>
            </source>
        """
    )

    with pytest.raises(
        XMLValidationError, match="Unknown child element <unknown> found in <known2>"
    ):
        validate_xml(source, spec)


def test_validates_with_empty_spec():
    spec: XMLSpec = {"child": {}}

    source = ET.fromstring(
        """
            <source>
                <child></child>
            </source>
        """
    )

    validate_xml(source, spec)


def test_does_not_raise_error_for_ignored_child():
    spec: XMLSpec = {"child": {"subchild": "$ANY_TEXT$", "ignoredchild": "$IGNORE$"}}

    source = ET.fromstring(
        """
            <source>
                <child>
                    <subchild>value</subchild>
                    <ignoredchild>
                        <ignoredsubchild>value</ignoredsubchild>
                        <otherignoredsubchild>value</otherignoredsubchild>
                    </ignoredchild>
                </child>
            </source>
        """
    )

    validate_xml(source, spec)


def test_does_not_raise_error_for_complete_publication_xml():
    spec: XMLSpec = fedora_publication_xml_spec

    source = read_source_xml("test/data/fedora/mock_publication_ultimate.xml")
    validate_xml(source, spec)


def test_error_can_contain_multiple_validation_errors():
    spec: XMLSpec = {"child": {"subchild": "$ANY_TEXT$"}, "child2": "$ANY_TEXT$"}

    source = ET.fromstring(
        """
            <source>
                <unknown1>value</unknown1>
                <child>
                    <subchild>value</subchild>
                    <unknown2>value</unknown2>
                </child>
            </source>
        """
    )

    with pytest.raises(
        XMLValidationError,
        match="Unknown child element <unknown1> found in <source>\nUnknown child element <unknown2> found in <child>",
    ):
        validate_xml(source, spec)


def test_specific_text_value_is_valid():
    spec: XMLSpec = {"child1": "someSpecificValue"}

    source = ET.fromstring(
        """
            <source>
                <child1>someSpecificValue</child1>
            </source>
        """
    )

    validate_xml(source, spec)


def test_specific_text_value_raises_error_when_other_text():
    spec: XMLSpec = {"child1": "someSpecificValue"}

    source = ET.fromstring(
        """
            <source>
                <child1>someOtherSpecificValue</child1>
            </source>
        """
    )
    with pytest.raises(
        XMLValidationError,
        match="Expected text content 'someSpecificValue' in <child1>, but found 'someOtherSpecificValue'",
    ):
        validate_xml(source, spec)


def test_specific_text_value_raises_error_when_object_instead_of_text():
    spec: XMLSpec = {"child1": "someSpecificValue"}

    source = ET.fromstring(
        """
            <source>
                <child1>
                    <subchild>value</subchild>
                </child1>
            </source>
        """
    )
    with pytest.raises(
        XMLValidationError,
        match="Expected text content 'someSpecificValue' in <child1>, but found child elements",
    ):
        validate_xml(source, spec)


def test_specific_text_value_valid_when_element_missing():
    spec: XMLSpec = {"child1": "someSpecificValue"}

    source = ET.fromstring(
        """
            <source>
            </source>
        """
    )
    validate_xml(source, spec)


def test_assert_empty_element_raises_when_child_element():
    spec: XMLSpec = {"child": "$EMPTY$"}

    source = ET.fromstring(
        """
            <source>
                <child><subchild>value</subchild></child>
            </source>
        """
    )
    with pytest.raises(
        XMLValidationError,
        match="Expected empty element <child>, but found child elements",
    ):
        validate_xml(source, spec)


def test_assert_empty_element_raises_when_text_content():
    spec: XMLSpec = {"child": "$EMPTY$"}

    source = ET.fromstring(
        """
            <source>
                <child>someText</child>
            </source>
        """
    )
    with pytest.raises(
        XMLValidationError,
        match="Expected empty element <child>, but found text content: someText",
    ):
        validate_xml(source, spec)


def test_validate_empty_element_self_closing_tag():
    spec: XMLSpec = {"child": "$EMPTY$"}

    source = ET.fromstring(
        """
            <source>
                <child/>
            </source>
        """
    )

    validate_xml(source, spec)


def test_validate_empty_element_empty_tag():
    spec: XMLSpec = {"child": "$EMPTY$"}

    source = ET.fromstring(
        """
            <source>
                <child></child>
            </source>
        """
    )

    validate_xml(source, spec)
