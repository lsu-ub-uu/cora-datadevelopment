import html
import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest
import requests

import scripts.create_new_validation_types as script
from common import validation_type_utils as common_utils


@pytest.fixture(autouse=True)
def reset_global_data(ctx, init_utils):
    script.CTX = None
    script.TOTAL_ERRORS = []
    script.TOTAL_UPDATES = 0
    script.TOTAL_UPDATES = 0
    script.TOTAL_CREATED = 0
    script.TOTAL_FETCHED = 0
    script.TOTAL_PROCESSED_RECORDS = 0
    script.CTX = ctx


def test_process_queue_and_add_note_to_map(sample_xml, monkeypatch):
    global_node_map = {}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return sample_xml

    def fake_collect_child_urls(node, root_url, url):
        return ["http://child_url", "http://another_child_url"]

    monkeypatch.setattr(common_utils, "fetch_record_as_xml", fake_fetch)
    monkeypatch.setattr(common_utils, "collect_child_urls", fake_collect_child_urls)

    common_utils.collect_nodes_from_root("http://root_url", global_node_map)
    assert called == True
    assert (
        global_node_map["http://root_url"].record_id == "__test_prefix_divaTextNewGroup"
    )


def test_process_and_possibly_save_not_saved_due_to_not_updated(
    record_node, monkeypatch
):
    monkeypatch.setattr(script, "is_already_processed", lambda node, mapping: False)
    monkeypatch.setattr(common_utils, "normalize_regex_patterns", lambda node: False)
    monkeypatch.setattr(
        common_utils,
        "normalize_child_reference_repeat",
        lambda node, record_info_groups: False,
    )
    monkeypatch.setattr(common_utils, "update_data_divider", lambda node: False)

    result = script.process_and_possibly_create(record_node, {"123": "XYZ_123"})
    assert result is False


def test_create_new_validation_types_for_record_type(monkeypatch, ctx, caplog):
    script.create_new_validation_types_for_record_type()

    assert any(
        "All records fetched: total unique records collected in node map: 2" in msg
        for msg in caplog.messages
    )
    assert any("=== Script finished ===" in msg for msg in caplog.messages)


def test_get_validation_types_to_process(monkeypatch):
    def fake_reply(type):
        return ["__test_prefix_some1"]

    monkeypatch.setattr(
        common_utils, "get_ids_for_record_type_matching_prefix", fake_reply
    )

    id_list = script.get_validation_types_to_process()
    assert "__test_prefix_some1" in id_list


def test_collect_record_info_children(create_node_tree):
    script.GLOBAL_NODE_MAP = create_node_tree
    script.collect_record_info_children()

    expected_children = {"urlC", "urlD", "urlE"}
    assert expected_children <= script.GLOBAL_INFO_CHILDREN.keys()


def test_process_node_create(record_node):
    script.process_node({"a": "b"}, record_node)
    assert script.TOTAL_CREATED == 1
    assert script.TOTAL_UPDATES == 0


def test_process_node_update(record_node):
    record_node.record_id = "a"
    script.EXISTING_VALIDATION_TYPES_WITH_PREFIX = ["a"]
    script.process_node({"a": "b"}, record_node)
    assert script.TOTAL_CREATED == 0
    assert script.TOTAL_UPDATES == 1


def test_process_node_exception(record_node, monkeypatch):
    monkeypatch.setattr(
        script,
        "process_and_possibly_create",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            requests.HTTPError("some exception")
        ),
    )

    script.process_node({"a": "b"}, record_node)

    assert script.TOTAL_CREATED == 0
    assert script.TOTAL_UPDATES == 0
    assert "Error processing divaTextNewGroup: some exception" in script.TOTAL_ERRORS


def test_process_and_possibly_update_dry_run(mock_top_level, record_node):
    script.DRY_RUN = True
    assert script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_update(init_utils, mock_top_level, monkeypatch):
    script.DRY_RUN = False

    monkeypatch.setattr(
        common_utils, "link_dependency_to_top_groups", lambda node, mapping=None: True
    )

    assert script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_update_already_processed(mock_top_level, monkeypatch):
    script.DRY_RUN = False
    monkeypatch.setattr(script, "is_already_processed", lambda *args, **kwargs: True)

    global_id_mapping = {"divaTextNewGroup": "some_new_id"}
    assert not script.process_and_possibly_update(mock_top_level, global_id_mapping)


def test_process_and_possibly_update_children_already_prefixed(
    mock_top_level, monkeypatch
):
    script.DRY_RUN = False

    monkeypatch.setattr(
        common_utils, "link_dependency_to_top_groups", lambda node, mapping=None: False
    )

    assert not script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_create_with_updated_final_value(record_node, monkeypatch):
    script.DRY_RUN = False
    script.RECORD_TYPE = "diva-output"
    script.TYPE_PREFIX = "__some_prefix_"

    monkeypatch.setattr(
        common_utils,
        "update_final_value_of_validation_type",
        lambda node, mapping=None: True,
    )
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda somebool: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda updateText: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda updateDefText: True)

    assert script.process_and_possibly_create(record_node, {"a": "b"})

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "__some_prefix_divaTextNewGroupText" in xml
    assert "__some_prefix_divaTextNewGroupDefText" in xml


def test_process_and_possibly_create_fail_because_record_info_child(
    record_node, monkeypatch
):
    script.DRY_RUN = False

    monkeypatch.setattr(
        common_utils, "record_is_a_child_of_info_group", lambda node, mapping=None: True
    )

    assert not script.process_and_possibly_create(record_node, {"a": "b"})


def test_unprocessed_nodes(monkeypatch):
    global_node_map = {"urlA": "nodeA"}
    processed = {}

    script.check_for_unprocessed_nodes(global_node_map, processed)

    assert "Warning: Record: urlA was never processed" in script.TOTAL_ERRORS


def test_collect_possible_final_value_node_doesnt_exist(record_node):
    script.collect_possible_final_value_node(record_node)
    assert len(script.FINAL_VALUE_NODES) == 0


def test_collect_possible_final_value_node_exist(record_node):
    metadata = record_node.xml_content.find("metadata")
    if metadata is None:
        metadata = ET.SubElement(record_node.xml_content, "metadata")
        final_value = ET.Element("finalValue")
        final_value.text = "some final value"
        metadata.append(final_value)

    script.collect_possible_final_value_node(record_node)

    assert script.FINAL_VALUE_NODES == {"divaTextNewGroup"}
    assert len(script.FINAL_VALUE_NODES) == 1


def test_process_node_map_bottom_up_and_store(create_node_tree, monkeypatch):
    node_tree = create_node_tree
    global_node_map = {
        "urlA": node_tree["A"],
        "urlD": node_tree["D"],
        "urlB": node_tree["B"],
        "urlE": node_tree["E"],
        "urlC": node_tree["C"],
    }

    script.GLOBAL_NODE_MAP = global_node_map

    processed_order = []

    def fake_process_node(mapping, node):
        processed_order.append(node.record_id)
        script.TOTAL_PROCESSED_RECORDS += 1
        return True

    monkeypatch.setattr(script, "process_node", fake_process_node)

    global_id_mapping = {"divaTextNewGroup": "some_new_id"}
    script.GLOBAL_ID_MAPPING = global_id_mapping

    script.process_node_map_bottom_up_and_store()

    assert script.TOTAL_PROCESSED_RECORDS == 5
    assert processed_order[0] == "E"
    assert processed_order[3] == "B"
    assert processed_order[4] == "A"
    assert set(processed_order) == {"E", "D", "C", "B", "A"}


def test_try_to_update_text(sample_text):
    changed = script.try_to_update_text(sample_text)

    assert changed is True
    text = ET.tostring(sample_text).decode("utf-8")
    assert "svensk text [Classic]" in text
    assert "norsk text [Classic]" in text
    assert "engelsk text [Classic]" in text


def test_try_to_update_def_text(sample_text):
    changed = script.try_to_update_def_text(sample_text)

    assert changed is True
    text = ET.tostring(sample_text).decode("utf-8")
    text = html.unescape(text)
    assert (
        "svensk text [Detta är en kopia som håller DiVA classics valideringsnivå]"
        in text
    )
    assert (
        "engelsk text [This is a copy that meets DiVA classics validation level.]"
        in text
    )
    assert (
        "norsk text [Dette er en kopi som oppfyller DiVA classics valideringsnivå.]"
        in text
    )


def test_get_text_node(sample_xml, monkeypatch):
    monkeypatch.setattr(common_utils, "fetch_record_as_xml", lambda xml: sample_xml)
    assert script.get_text_node("some_id") is not None


def test_possibly_create_new_texts_for_updated_records(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)

    script.possibly_create_new_texts_for_updated_records(record_node)

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "__some_prefix_divaTextNewGroupText" in xml
    assert "__some_prefix_divaTextNewGroupDefText" in xml


def test_possibly_create_new_texts_for_updated_records_not_validation_type(
    record_node, monkeypatch
):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: False
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)

    script.possibly_create_new_texts_for_updated_records(record_node)

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "__some_prefix_divaTextNewGroupText" not in xml
    assert "__some_prefix_divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_for_text_id(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)

    script.create_new_texts_for_updated_records(
        record_node, ".//textId", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "__some_prefix_divaTextNewGroupText" in xml
    assert "divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_for_def_text_id(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)

    script.create_new_texts_for_updated_records(
        record_node, ".//defTextId", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "divaTextNewGroupText" in xml
    assert "__some_prefix_divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_xpath_not_found(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)

    assert not script.create_new_texts_for_updated_records(
        record_node, ".//not_text_id", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "divaTextNewGroupText" in xml
    assert "divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_not_valid_record_id(
    record_node, monkeypatch
):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)
    monkeypatch.setattr(script, "not_a_valid_linked_record_id", lambda node: True)

    assert not script.create_new_texts_for_updated_records(
        record_node, ".//defTextId", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "divaTextNewGroupText" in xml
    assert "divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_already_updated(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)
    monkeypatch.setattr(script, "not_a_valid_linked_record_id", lambda node: False)
    script.UPDATED_TEXTS.add("divaTextNewGroupDefText")

    assert not script.create_new_texts_for_updated_records(
        record_node, ".//defTextId", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "divaTextNewGroupText" in xml
    assert "divaTextNewGroupDefText" in xml


def test_create_new_texts_for_updated_records_no_text_parts(record_node, monkeypatch):
    script.TYPE_PREFIX = "__some_prefix_"
    monkeypatch.setattr(
        script, "validation_type_validates_target_record_type", lambda node: True
    )
    monkeypatch.setattr(script, "try_to_update_text", lambda node: True)
    monkeypatch.setattr(script, "try_to_update_def_text", lambda node: True)
    monkeypatch.setattr(script, "not_a_valid_linked_record_id", lambda node: False)
    monkeypatch.setattr(script, "try_to_update_text", lambda node: False)

    assert not script.create_new_texts_for_updated_records(
        record_node, ".//defTextId", script.try_to_update_text
    )

    xml = ET.tostring(record_node.xml_content).decode("utf-8")
    xml = html.unescape(xml)
    assert "divaTextNewGroupText" in xml
    assert "divaTextNewGroupDefText" in xml


def test_main(monkeypatch, ctx):
    fake_args = SimpleNamespace(
        system="testSystem",
        login_id="user",
        app_token="token",
        cora_url=None,
        workers=1,
        prefix="__XYZ_",
        recordtype="diva-output",
        datadivider="diva",
        apply=False,
    )

    monkeypatch.setattr(
        script,
        "create_argument_parser",
        lambda **kwargs: SimpleNamespace(parse_args=lambda: fake_args),
    )
    monkeypatch.setattr(script, "CoraContext", lambda **kwargs: ctx)

    script.main()

    assert script.CTX is ctx
