from unittest.mock import MagicMock
from xml.etree import ElementTree as ET
from cora.context import MockContext
from fedora_to_cora.process_fedora_publication_files import (
    process_fedora_publication_files,
)


def test_process_fedora_publication_files(monkeypatch):
    xml_dir = "test/xml"
    system = "test_system"
    login_id = "test_login"
    app_token = "test_token"
    dry_run = True

    mock_read_source_xml = MagicMock(return_value=ET.Element("publication"))
    monkeypatch.setattr(
        "fedora_to_cora.process_fedora_publication_files.read_source_xml",
        mock_read_source_xml,
    )
    mock_context = MockContext()
    monkeypatch.setattr(
        "fedora_to_cora.process_fedora_publication_files.CoraContext",
        MagicMock(return_value=mock_context),
    )

    monkeypatch.setattr(
        "os.listdir", MagicMock(return_value=["test1.xml", "test2.xml", "test3.xml"])
    )

    monkeypatch.setattr(
        "fedora_to_cora.process_fedora_publication_files.run_with_threads",
        lambda items, func, workers, desc: [func(item) for item in items],
    )

    output_migrate_mock = MagicMock(
        side_effect=[
            (True, []),  # test1.xml - success
            (False, ["validation error"]),  # test2.xml - failure
            (True, []),  # test3.xml - success
        ]
    )
    monkeypatch.setattr(
        "fedora_to_cora.process_fedora_publication_files.output_migrate",
        output_migrate_mock,
    )

    process_fedora_publication_files(xml_dir, system, login_id, app_token, dry_run)

    assert output_migrate_mock.call_count == 3

    mock_context.log.assert_any_call("✅ test1.xml")  # type: ignore
    mock_context.log.assert_any_call("❌ test2.xml - Errors: [validation error]")  # type: ignore
    mock_context.log.assert_any_call("✅ test3.xml")  # type: ignore
