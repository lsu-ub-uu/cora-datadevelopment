import pytest
from tqdm import tqdm

import scripts.delete_new_validation_types as script
from common import validation_type_utils as common_utils


@pytest.fixture(autouse=True)
def reset_global_data(ctx, init_utils):
    script.TYPE_PREFIX = "__test_prefix_"
    script.GLOBAL_NODE_MAP.clear()
    script.GLOBAL_ID_MAPPING.clear()
    script.GLOBAL_RECORD_INFO_CHILDREN.clear()
    script.TOTAL_PREFIX_MATCHES = 0
    script.TOTAL_PROCESSED_RECORDS = 0
    script.TOTAL_RECORD_DELETIONS = 0
    script.TOTAL_RECORD_UPDATES = 0
    script.TOTAL_PRESENTATION_DELETIONS = 0
    script.TOTAL_ERRORS.clear()
    script.BLACKLIST_TYPES = ["diva-output", "tempContainerOutput"]
    script.CTX = ctx


def test_delete_records_with_prefix(monkeypatch, record_node):
    def fake_get_ids(prefix):
        fake_presentations = ["__test_prefix_presentation1", "__test_prefix_presentation2"]
        fake_validation_types = ["__test_prefix_record1", "__test_prefix_record2", "__test_prefix_record3"]

        if prefix == "presentation":
            return fake_presentations
        else:
            return fake_validation_types

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)

    script.delete_records_with_prefix()
    assert script.TOTAL_PROCESSED_RECORDS == 3
    assert script.TOTAL_RECORD_DELETIONS == 3


def test_delete_records_with_prefix_no_validation_types(monkeypatch):
    def fake_get_ids(prefix):
        fake_presentations = ["__test_prefix_presentation1", "__test_prefix_presentation2"]
        fake_validation_types = []

        if prefix == "presentation":
            return fake_presentations
        else:
            return fake_validation_types

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)

    script.delete_records_with_prefix()
    assert script.TOTAL_PROCESSED_RECORDS == 0
    assert script.TOTAL_RECORD_DELETIONS == 0


def test_delete_presentations_dry_run(monkeypatch):
    script.DRY_RUN = True
    script.delete_records_of_type_matching_prefix("presentation")


def test_delete_presentations(monkeypatch):
    script.DRY_RUN = False

    def fake_get_ids(prefix):
        return ["__test_prefix_presentation1", "__test_prefix_presentation2"]

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)
    monkeypatch.setattr(script.utils, "try_to_delete_record", lambda url, errors: True)

    script.delete_records_of_type_matching_prefix("presentation")
    assert script.TOTAL_RECORD_DELETIONS == 2


def test_delete_presentations_no_presentations(monkeypatch):
    script.DRY_RUN = False

    def fake_get_ids(prefix):
        return []

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)
    monkeypatch.setattr(script.utils, "try_to_delete_record", lambda url, errors: False)

    script.delete_records_of_type_matching_prefix("presentation")
    assert script.TOTAL_RECORD_DELETIONS == 0


def test_delete_presentations_no_presentations_with_retry(monkeypatch, ctx):
    script.DRY_RUN = False

    def fake_get_ids(prefix):
        return ["__test_prefix_presentation1", "__test_prefix_presentation2"]

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)
    delete_sequence = iter([False, False, True])
    monkeypatch.setattr(script.utils, "try_to_delete_record",
                        lambda url, errors: next(delete_sequence, True))

    script.delete_records_of_type_matching_prefix("presentation")
    assert script.TOTAL_RECORD_DELETIONS == 2

    calls = [call.args[0] for call in ctx.log.mock_calls]
    assert any("Failed to delete record" in msg for msg in calls)
    assert len(calls) == 2


def test_delete_presentations_no_presentations_failed_delete(monkeypatch, ctx):
    script.DRY_RUN = False

    def fake_get_ids(prefix):
        return ["__test_prefix_presentation1"]

    monkeypatch.setattr(common_utils, "get_ids_for_record_type_matching_prefix", fake_get_ids)
    delete_sequence = iter([False, False, True])
    monkeypatch.setattr(script.utils, "try_to_delete_record",
                        lambda url, errors: False)

    script.delete_records_of_type_matching_prefix("presentation")
    assert script.TOTAL_RECORD_DELETIONS == 0

    calls = [call.args[0] for call in ctx.log.mock_calls]
    assert any("Failed to delete record" in msg for msg in calls)
    assert len(calls) == 5

    assert "Failed to delete http://baseUrl/presentation/__test_prefix_presentation1 after 5 retries!" in script.TOTAL_ERRORS


def test_process_node_map_and_delete_records(create_node_tree, monkeypatch):
    node_tree = create_node_tree
    global_node_map = {
        "urlA": node_tree["A"],
        "urlD": node_tree["D"],
        "urlB": node_tree["B"],
        "urlE": node_tree["E"],
        "urlC": node_tree["C"]
    }

    processed_order = []

    def fake_process_node(mapping, node):
        processed_order.append(node.record_id)
        return True

    monkeypatch.setattr(script, "process_record", fake_process_node)

    script.process_node_map_and_delete_records(global_node_map)

    assert script.TOTAL_PROCESSED_RECORDS == 5
    assert processed_order[0] == "A"
    assert processed_order[1] == "B"
    assert processed_order[4] == "E"
    assert set(processed_order) == {"E", "D", "C", "B", "A"}


def test_collect_text_ids(monkeypatch, record_node):
    expected_ids = {"divaTextNewGroupText", "divaTextNewGroupDefText"}

    script.collect_text_ids(record_node)
    assert script.VALIDATION_TYPE_TEXTS is not None
    assert all(record_id in script.VALIDATION_TYPE_TEXTS for record_id in expected_ids)


def test_check_for_unprocessed_nodes(monkeypatch, record_node):
    global_node_map = {"some_url": record_node}
    processed = {"other_url"}
    script.check_for_unprocessed_nodes(global_node_map, processed)
    assert "Warning: Record: some_url was never processed" in script.TOTAL_ERRORS


def test_prepare_url_and_possibly_delete_fail_due_to_not_prefixed(record_node):
    script.DRY_RUN = False
    record_node.record_id = "no_prefix_to_be_seen"
    assert not script.prepare_url_and_possibly_delete(record_node)


def test_prepare_url_and_possibly_delete_success_due_to_correct_prefix(record_node):
    script.DRY_RUN = False
    record_node.record_id = "__test_prefix_buhbye"
    assert script.prepare_url_and_possibly_delete(record_node)


def test_update_record_dry_run(record_node, ctx):
    script.DRY_RUN = True
    assert script.update_record(record_node)

    calls = [call.args[0] for call in ctx.log.mock_calls]
    assert any("Dry run mode" in msg for msg in calls)


def test_update_record(record_node):
    script.DRY_RUN = False
    assert script.update_record(record_node)


def test_process_record_expect_update(record_node):
    script.process_record(tqdm(total=1), record_node)
    assert script.TOTAL_RECORD_UPDATES == 1
