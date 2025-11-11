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


def test_get_validation_types_to_process():
    assert script.get_validation_types_to_process()


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
    assert global_node_map["http://root_url"].record_id == "__test_prefix_divaTextNewGroup"


def test_process_and_possibly_save_not_saved_due_to_not_updated(record_node, monkeypatch):
    monkeypatch.setattr(script, "is_already_processed", lambda node, mapping: False)
    monkeypatch.setattr(common_utils, "normalize_regex_patterns", lambda node: False)
    monkeypatch.setattr(common_utils, "normalize_child_reference_repeat", lambda node: False)
    monkeypatch.setattr(common_utils, "update_data_divider", lambda node: False)

    result = script.process_and_possibly_create(record_node, {"123": "XYZ_123"})
    assert result is False


def test_create_new_validation_types_for_record_type(monkeypatch, ctx):
    script.create_new_validation_types_for_record_type()

    calls = [call.args[0] for call in ctx.log.mock_calls]
    assert any("All records fetched: total unique records collected in node map: 2" in msg for msg in calls)
    assert any("=== Script finished ===" in msg for msg in calls)


def test_get_validation_types_to_process2(monkeypatch):
    def fake_reply(type):
        return ["__test_prefix_some1"]

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_reply)

    id_list = script.get_validation_types_to_process()
    assert "__test_prefix_some1" in id_list


def test_collect_record_info_children(create_node_tree):
    script.GLOBAL_NODE_MAP = create_node_tree
    script.collect_record_info_children()

    expected_children = {"urlC", "urlD", "urlE"}
    assert expected_children <= script.GLOBAL_RECORD_INFO_CHILDREN.keys()


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
        script, "process_and_possibly_create", lambda *args, **kwargs: (_ for _ in ())
        .throw(requests.HTTPError("some exception")))

    script.process_node({"a": "b"}, record_node)

    assert script.TOTAL_CREATED == 0
    assert script.TOTAL_UPDATES == 0
    assert "Error processing divaTextNewGroup: some exception" in script.TOTAL_ERRORS


def test_process_and_possibly_update_dry_run(mock_top_level, record_node):
    script.DRY_RUN = True
    assert script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_update(init_utils, mock_top_level, monkeypatch):
    script.DRY_RUN = False

    monkeypatch.setattr(common_utils, "link_dependency_to_top_groups", lambda node, mapping=None: True)

    assert script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_update_already_processed(mock_top_level, monkeypatch):
    script.DRY_RUN = False
    monkeypatch.setattr(script, "is_already_processed", lambda *args, **kwargs: True)

    global_id_mapping = {"divaTextNewGroup": "some_new_id"}
    assert not script.process_and_possibly_update(mock_top_level, global_id_mapping)


def test_process_and_possibly_update_children_already_prefixed(mock_top_level, monkeypatch):
    script.DRY_RUN = False

    monkeypatch.setattr(common_utils, "link_dependency_to_top_groups", lambda node, mapping=None: False)

    assert not script.process_and_possibly_update(mock_top_level, {"a": "b"})


def test_process_and_possibly_create_with_updated_final_value(record_node, monkeypatch):
    script.DRY_RUN = False

    monkeypatch.setattr(common_utils, "update_final_value_of_validation_type", lambda node, mapping=None: True)

    assert script.process_and_possibly_create(record_node, {"a": "b"})


def test_process_and_possibly_create_fail_because_record_info_child(record_node, monkeypatch):
    script.DRY_RUN = False

    monkeypatch.setattr(common_utils, "record_is_a_child_of_record_info", lambda node, mapping=None: True)

    assert not script.process_and_possibly_create(record_node, {"a": "b"})


def test_unprocessed_nodes(monkeypatch):
    global_node_map = {"urlA": "nodeA"}
    processed = {}

    script.check_for_unprocessed_nodes(global_node_map, processed)

    assert "Warning: Record: urlA was never processed" in script.TOTAL_ERRORS


def test_process_node_map_bottom_up_and_store(create_node_tree, monkeypatch):
    node_tree = create_node_tree
    global_node_map = {
        "urlA": node_tree["A"],
        "urlD": node_tree["D"],
        "urlB": node_tree["B"],
        "urlE": node_tree["E"],
        "urlC": node_tree["C"]
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


def test_main(monkeypatch, ctx):
    fake_args = SimpleNamespace(
        system="testSystem",
        login_id="user",
        app_token="token",
        workers=1,
        prefix="__XYZ_",
        recordtype="diva-output",
        datadivider="diva",
        apply=False
    )

    monkeypatch.setattr(script, "create_argument_parser",
                        lambda **kwargs: SimpleNamespace(parse_args=lambda: fake_args))
    monkeypatch.setattr(script, "CoraContext", lambda **kwargs: ctx)

    script.main()

    assert script.CTX is ctx
