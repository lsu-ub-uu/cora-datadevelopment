import xml.etree.ElementTree as ET
from unittest.mock import patch

from scripts.util import find_tag


def test_is_empty_tag_recognizes_self_closing_and_paired_tags():
    self_closing_tag = ET.fromstring("<tag />")
    paired_tag = ET.fromstring("<tag></tag>")

    assert find_tag._is_empty_tag(self_closing_tag)
    assert find_tag._is_empty_tag(paired_tag)


@patch("scripts.util.find_tag._read_source_records")
@patch("scripts.util.find_tag.logging.basicConfig")
@patch("scripts.util.find_tag.logging.info")
@patch("scripts.util.find_tag.pretty_print_xml", return_value="<doi><child /></doi>")
def test_main_includes_empty_tag_count_in_summary(
    mock_pretty_print_xml,
    mock_info,
    mock_basic_config,
    mock_read_source_records,
    capsys,
):
    record = ET.fromstring(
        "<record><pid>record-1</pid><importSource>legacy</importSource>"
        "<publicationType><publicationTypeCode>article</publicationTypeCode></publicationType>"
        "<doi /><doi></doi><doi>text</doi><doi><child /></doi>"
        "<identifiers><entry><publicationIdentifierType>doi</publicationIdentifierType>"
        "<publicationIdentifier><value>10.1234/doi</value></publicationIdentifier></entry>"
        "<entry><publicationIdentifierType>libris</publicationIdentifierType>"
        "<publicationIdentifier><value>libris-value</value></publicationIdentifier></entry>"
        "</identifiers></record>"
    )
    mock_read_source_records.return_value = [record]

    with patch(
        "scripts.util.find_tag.path_to_look_for",
        [
            "./doi",
            "./identifiers/entry[publicationIdentifierType='doi']/publicationIdentifier/value",
        ],
    ):
        find_tag.main()

    output = capsys.readouterr().out
    assert "[record-1] Found match at path ./doi[3] with text: text" in output
    assert (
        "[record-1] Found match at path ./identifiers/entry[1]/publicationIdentifier/value "
        "with text: 10.1234/doi"
    ) in output
    assert "libris-value" not in output
    assert (
        "Found 3 non-empty tags matching paths ./doi, "
        "./identifiers/entry[publicationIdentifierType='doi']/publicationIdentifier/value, "
        "and 2 empty tags"
    ) in output

    mock_read_source_records.assert_called_once_with(find_tag.xml_dir)
    mock_pretty_print_xml.assert_called_once_with(record.findall("./doi")[3])
    logged_messages = [call.args[0] for call in mock_info.call_args_list]
    assert (
        "[record-1] Found match at path ./doi[4] with child elements: ['child']"
    ) in logged_messages
    assert "<doi><child /></doi>" in logged_messages
    assert logged_messages.count("Import source: legacy") == 5
    assert logged_messages.count("PublicationType: article") == 5
    assert logged_messages[-1] == (
        "\nFound 3 non-empty tags matching paths ./doi, "
        "./identifiers/entry[publicationIdentifierType='doi']/publicationIdentifier/value, "
        "and 2 empty tags"
    )


def test_read_source_records_reads_only_xml_files(tmp_path):
    (tmp_path / "record.xml").write_text("<record />", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not XML", encoding="utf-8")

    records = find_tag._read_source_records(str(tmp_path))

    assert len(records) == 1
    assert records[0].tag == "record"
