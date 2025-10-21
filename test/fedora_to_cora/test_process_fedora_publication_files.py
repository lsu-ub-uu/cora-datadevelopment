from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET
from common.xml_validate import XMLValidationError
from cora.context import MockContext
from fedora_to_cora.process_fedora_publication_files import (
    process_fedora_publication_files,
)


@patch("fedora_to_cora.process_fedora_publication_files.output_migrate")
@patch("fedora_to_cora.process_fedora_publication_files.run_with_threads")
@patch("os.listdir")
@patch("fedora_to_cora.process_fedora_publication_files.read_source_xml")
@patch("fedora_to_cora.process_fedora_publication_files.validate_xml")
def test_process_fedora_publication_files(
    mock_validate_xml,
    mock_read_source_xml,
    mock_listdir,
    mock_run_with_threads,
    mock_output_migrate,
):
    xml_dir = "test/xml"
    mock_context = MockContext()
    apply = False

    mock_read_source_xml.side_effect = [
        ET.fromstring("<publication><pid>test1</pid></publication>"),
        ET.fromstring("<publication><pid>test2</pid></publication>"),
        ET.fromstring("<publication><pid>test3</pid></publication>"),
    ]
    mock_listdir.return_value = ["test1.xml", "test2.xml", "test3.xml"]
    mock_run_with_threads.side_effect = lambda items, func, workers, desc: [
        func(item) for item in items
    ]

    mock_output_migrate.side_effect = [
        (True, []),  # test1.xml - success
        (False, ["validation error"]),  # test2.xml - failure
        (True, []),  # test3.xml - success
    ]

    process_fedora_publication_files(xml_dir, mock_context, apply)

    assert mock_output_migrate.call_count == 3

    mock_context.log.assert_any_call("✅ test1")  # type: ignore
    mock_context.log.assert_any_call("❌ test2 - Errors: [validation error]")  # type: ignore
    mock_context.log.assert_any_call("✅ test3")  # type: ignore


@patch("fedora_to_cora.process_fedora_publication_files.output_migrate")
@patch("fedora_to_cora.process_fedora_publication_files.run_with_threads")
@patch("os.listdir")
@patch("fedora_to_cora.process_fedora_publication_files.read_source_xml")
@patch("fedora_to_cora.process_fedora_publication_files.validate_xml")
def test_handles_raised_exception_in_processing(
    mock_validate_xml,
    mock_read_source_xml,
    mock_listdir,
    mock_run_with_threads,
    mock_output_migrate,
):
    xml_dir = "test/xml"
    apply = False
    mock_context = MockContext()

    mock_read_source_xml.side_effect = [
        ET.fromstring("<publication><pid>test1</pid></publication>"),
        ET.fromstring("<publication><pid>test2</pid></publication>"),
        ET.fromstring("<publication><pid>test3</pid></publication>"),
    ]
    mock_listdir.return_value = ["test1.xml", "test2.xml", "test3.xml"]
    mock_run_with_threads.side_effect = lambda items, func, workers, desc: [
        func(item) for item in items
    ]

    mock_output_migrate.side_effect = [
        (True, []),
        Exception("Something went wrong during migration"),
        (True, []),
    ]

    process_fedora_publication_files(xml_dir, mock_context, apply)

    assert mock_output_migrate.call_count == 3

    mock_context.log.assert_any_call("✅ test1")  # type: ignore
    mock_context.log.assert_any_call("❌ test2 - Exception: Something went wrong during migration")  # type: ignore
    mock_context.log.assert_any_call("✅ test3")  # type: ignore


@patch("fedora_to_cora.process_fedora_publication_files.output_migrate")
@patch("fedora_to_cora.process_fedora_publication_files.run_with_threads")
@patch("os.listdir")
@patch("fedora_to_cora.process_fedora_publication_files.read_source_xml")
@patch("fedora_to_cora.process_fedora_publication_files.validate_xml")
def test_does_not_start_migrating_when_any_xml_validation_fails(
    mock_validate_xml,
    mock_read_source_xml,
    mock_listdir,
    mock_run_with_threads,
    mock_output_migrate,
):
    xml_dir = "test/xml"
    apply = False
    mock_context = MockContext()

    mock_read_source_xml.side_effect = [
        ET.fromstring("<publication><pid>test1</pid></publication>"),
        ET.fromstring("<publication><pid>test2</pid></publication>"),
        ET.fromstring("<publication><pid>test3</pid></publication>"),
    ]
    mock_listdir.return_value = ["test1.xml", "test2.xml", "test3.xml"]
    mock_run_with_threads.side_effect = lambda items, func, workers, desc: [
        func(item) for item in items
    ]

    mock_validate_xml.side_effect = (
        None,
        XMLValidationError("Some xml validation error"),
        XMLValidationError("Some other xml validation error"),
    )

    process_fedora_publication_files(xml_dir, mock_context, apply)

    assert mock_validate_xml.call_count == 3
    assert mock_output_migrate.call_count == 0
    mock_context.log.assert_any_call("==== Skipped migration due to XML Validation Error in source data ==== ")  # type: ignore
    mock_context.log.assert_any_call("❌ test2 - XML Validation Error: Some xml validation error")  # type: ignore
    mock_context.log.assert_any_call("❌ test3 - XML Validation Error: Some other xml validation error")  # type: ignore

@patch("fedora_to_cora.process_fedora_publication_files.output_migrate")
@patch("fedora_to_cora.process_fedora_publication_files.run_with_threads")
@patch("os.listdir")
@patch("fedora_to_cora.process_fedora_publication_files.read_source_xml")
@patch("fedora_to_cora.process_fedora_publication_files.validate_xml")
def test_process_fedora_publication_files_with_limit(
    mock_validate_xml,
    mock_read_source_xml,
    mock_listdir,
    mock_run_with_threads,
    mock_output_migrate,
):
    xml_dir = "test/xml"
    mock_context = MockContext()
    apply = False

    mock_read_source_xml.side_effect = [
        ET.fromstring("<publication><pid>test1</pid></publication>"),
        ET.fromstring("<publication><pid>test2</pid></publication>"),
        ET.fromstring("<publication><pid>test3</pid></publication>"),
    ]
    mock_listdir.return_value = ["test1.xml", "test2.xml", "test3.xml"]
    mock_run_with_threads.side_effect = lambda items, func, workers, desc: [
        func(item) for item in items
    ]

    mock_output_migrate.side_effect = [
        (True, []),  # test1.xml - success
        (False, ["validation error"]),  # test2.xml - failure
        (True, []),  # test3.xml - success
    ]

    process_fedora_publication_files(xml_dir, mock_context, apply, limit=2)

    assert mock_output_migrate.call_count == 2

    mock_context.log.assert_any_call("✅ test1")  # type: ignore
    mock_context.log.assert_any_call("❌ test2 - Errors: [validation error]")  # type: ignore
