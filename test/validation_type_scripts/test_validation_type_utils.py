import xml.etree.ElementTree as ET

import pytest

from common import validation_type_utils as common_utils


@pytest.fixture(autouse=True)
def init_stuff(init_utils):
    print("init stuff")


def test_get_root_urls_for_validation_types(init_utils):
    root_urls = common_utils.get_root_urls_for_validation_types(["someType"])
    assert "http://baseUrl/validationType/someType" in root_urls


def test_build_node_map_from_child_references_new_url_added(record_node, monkeypatch):
    global_node_map = {}

    def fake_collect_nodes_from_root(root_url, node_map):
        node_map[root_url] = record_node

    monkeypatch.setattr(common_utils, "collect_nodes_from_root", fake_collect_nodes_from_root)

    common_utils.build_node_map_from_child_references("http://root_url", global_node_map)
    assert len(global_node_map) == 1
    assert "http://root_url" in global_node_map


def test_build_node_map_from_child_references_root_url_already_in_map(record_node):
    global_node_map = {"root_url": record_node}
    common_utils.build_node_map_from_child_references("root_url", global_node_map)
    assert len(global_node_map) == 1


def test_process_queue_already_in_node_map(record_node, monkeypatch):
    global_node_map = {"http://root_url": record_node}
    called = False

    def fake_fetch(url):
        nonlocal called
        called = True
        return "<xml></xml>"

    monkeypatch.setattr(common_utils, "fetch_record_as_xml", fake_fetch)
    common_utils.collect_nodes_from_root("http://root_url", global_node_map)
    assert called == False


def test_collect_nodes_from_root_with_child_urls(monkeypatch, record_node):
    root_url = "http://root_url"
    child_url = "http://child_url"
    global_node_map = {}

    monkeypatch.setattr(common_utils, "fetch_record_as_xml", lambda url: "<xml></xml>")
    monkeypatch.setattr(common_utils, "parse_record_from_xml", lambda xml, url: record_node)

    def fake_collect_child_urls(node, root, url):
        return [child_url] if url == root_url else []

    monkeypatch.setattr(common_utils, "collect_child_urls", fake_collect_child_urls)

    common_utils.collect_nodes_from_root(root_url, global_node_map)

    assert root_url in global_node_map
    assert child_url in global_node_map
    assert global_node_map[root_url] is record_node
    assert global_node_map[child_url] is record_node
    assert len(global_node_map) == 2


def test_link_parent_child_relationship(create_node_tree):
    node_map = {node.url: node for node in create_node_tree.values()}

    for node in node_map.values():
        node.children = []
        node.parents = []

    node_map["urlA"].child_urls = ["urlC", "urlD"]
    node_map["urlB"].child_urls = ["urlE"]
    node_map["urlC"].child_urls = ["urlE"]
    node_map["urlD"].child_urls = ["urlE"]
    node_map["urlE"].child_urls = []

    common_utils.link_parent_child_relationship(node_map)

    assert set(child.url for child in node_map["urlA"].children) == {"urlC", "urlD"}
    assert set(child.url for child in node_map["urlB"].children) == {"urlE"}
    assert set(child.url for child in node_map["urlC"].children) == {"urlE"}
    assert set(child.url for child in node_map["urlD"].children) == {"urlE"}
    assert node_map["urlE"].children == []

    assert set(parent.url for parent in node_map["urlC"].parents) == {"urlA"}
    assert set(parent.url for parent in node_map["urlD"].parents) == {"urlA"}
    assert set(parent.url for parent in node_map["urlE"].parents) == {"urlB", "urlC", "urlD"}
    assert node_map["urlA"].parents == []
    assert node_map["urlB"].parents == []


def test_record_info_group_true():
    xml_str = """
    <root>
        <metadata type="group">
            <nameInData>recordInfo</nameInData>
        </metadata>
    </root>
    """
    record_info = ET.fromstring(xml_str)
    assert common_utils.info_groups(record_info) is True


def test_record_info_group_wrong_name():
    xml_str = """
    <root>
        <metadata type="group">
            <nameInData>otherName</nameInData>
        </metadata>
    </root>
    """
    not_record_info = ET.fromstring(xml_str)
    assert common_utils.info_groups(not_record_info) is False


def test_record_is_a_child_of_record_info(record_node):
    record_node.url = "http://this_is_a_record_info_child"
    assert common_utils.record_is_a_child_of_info_group(record_node,
                                                        {"http://this_is_a_record_info_child": "someNode"})


def test_record_is_not_a_child_of_record_info(record_node):
    record_node.url = "http://this_is_NOT_record_info_child"
    assert not common_utils.record_is_a_child_of_info_group(record_node, {
        "http://just_an_actual_glorious_record_info_child": "someNode"})


def test_update_final_value_success(init_utils):
    xml = """
    <record>
        <metadata type="recordLink">
            <nameInData>validationType</nameInData>
            <finalValue>some_value</finalValue>
        </metadata>
    </record>
    """
    record = ET.fromstring(xml)
    common_utils.update_final_value_of_validation_type(record)

    final_value = record.find(".//metadata[@type='recordLink']/finalValue")
    assert final_value.text == "__test_prefix_some_value"


def test_update_final_value_no_update(init_utils):
    xml = """
    <record>
        <metadata type="recordLink">
            <nameInData>not_a_validation_type</nameInData>
            <finalValue>some_sacred_value</finalValue>
        </metadata>
    </record>
    """
    record = ET.fromstring(xml)
    assert not common_utils.update_final_value_of_validation_type(record)


def test_possibly_update_data_of_non_record_info_child_false(record_node, monkeypatch):
    record_info_groups = {"some_record_info_group"}
    final_value_nodes = {"some_final_value_node"}
    monkeypatch.setattr(common_utils, "set_data_quality_to_classic", lambda node: False)
    monkeypatch.setattr(common_utils, "normalize_regex_patterns", lambda node: False)
    monkeypatch.setattr(common_utils, "normalize_child_reference_repeat", lambda node, groups: False)
    assert not common_utils.possibly_update_data_of_non_info_group_child(record_node, record_info_groups,
                                                                         final_value_nodes, False)


def test_possibly_update_data_of_non_record_info_child_true_1(record_node, monkeypatch):
    record_info_groups = {"some_record_info_group"}
    final_value_nodes = {"some_final_value_node"}
    monkeypatch.setattr(common_utils, "set_data_quality_to_classic", lambda node: True)
    monkeypatch.setattr(common_utils, "normalize_regex_patterns", lambda node: False)
    monkeypatch.setattr(common_utils, "normalize_child_reference_repeat", lambda node, groups: False)
    assert common_utils.possibly_update_data_of_non_info_group_child(record_node, record_info_groups, final_value_nodes,
                                                                     False)


def test_possibly_update_data_of_non_record_info_child_true_2(record_node, monkeypatch):
    record_info_groups = {"some_record_info_group"}
    final_value_nodes = {"some_final_value_node"}
    monkeypatch.setattr(common_utils, "set_data_quality_to_classic", lambda node: False)
    monkeypatch.setattr(common_utils, "normalize_regex_patterns", lambda node: True)
    monkeypatch.setattr(common_utils, "normalize_child_reference_repeat", lambda node, groups: True)
    assert common_utils.possibly_update_data_of_non_info_group_child(record_node, record_info_groups, final_value_nodes,
                                                                     False)


def test_set_data_quality_to_classic():
    xml = """
    <record>
        <metadata>
            <nameInData>dataQuality</nameInData>
            <finalValue>cora2026</finalValue>
        </metadata>
    </record>
    """
    record = ET.fromstring(xml)

    assert common_utils.set_data_quality_to_classic(record)
    final_value = record.find(".//metadata/finalValue")
    assert final_value.text == "classic"


def test_set_data_quality_to_classic_false():
    xml = """
    <record>
        <metadata>
            <nameInData>not_data_Quality</nameInData>
            <finalValue>cora2026</finalValue>
        </metadata>
    </record>
    """
    record = ET.fromstring(xml)

    assert not common_utils.set_data_quality_to_classic(record)
    final_value = record.find(".//metadata/finalValue")
    assert final_value.text == "cora2026"


def test_normalize_regex_patterns(record_node, monkeypatch):
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: False)
    updated = common_utils.normalize_regex_patterns(record_node.xml_content)
    regex_text = record_node.xml_content.find(".//regEx").text
    assert updated
    assert regex_text == r"^\S.*$"


def test_normalize_regex_patterns_ignore_variant(record_node, monkeypatch):
    regex = record_node.xml_content.find(".//regEx")
    regex.text = r"^[\s\S]+$"
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: False)
    updated = common_utils.normalize_regex_patterns(record_node.xml_content)
    regex_text = record_node.xml_content.find(".//regEx").text
    assert not updated
    assert regex_text == r"^[\s\S]+$"


def test_normalize_regex_patterns_record_info_child(record_node, monkeypatch):
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: True)
    updated = common_utils.normalize_regex_patterns(record_node.xml_content)
    regex_text = record_node.xml_content.find(".//regEx").text
    assert not updated
    assert regex_text == r"(.*Text$)"


def test_normalize_child_reference_repeat(monkeypatch, record_node):
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: False)

    assert common_utils.normalize_child_reference_repeat(record_node.xml_content, {"some_record_info_group"})
    child = record_node.xml_content.find(".//childReference")
    assert child.find("repeatMin").text == "0"
    assert child.find("repeatMax").text == "1"


def test_normalize_child_reference_repeat_record_info_child(monkeypatch, record_node):
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: True)

    assert not common_utils.normalize_child_reference_repeat(record_node.xml_content, {"some_record_info_group"})

    child = record_node.xml_content.find(".//childReference")
    assert child.find("repeatMin").text == "1"
    assert child.find("repeatMax").text == "1"


def test_normalize_child_reference_repeat_record_info_child_no_update_due_to_record_info_group(monkeypatch,
                                                                                               mock_top_level):
    monkeypatch.setattr(common_utils, "info_groups", lambda boolean: False)

    assert common_utils.normalize_child_reference_repeat(mock_top_level.xml_content, {"recordInfoNewDivaTextGroup"})

    record_info_reference = None
    for child_reference in mock_top_level.xml_content.findall(".//childReference"):
        if child_reference.findtext(".//linkedRecordId") == "recordInfoNewDivaTextGroup":
            record_info_reference = child_reference
            break

    assert record_info_reference.find("repeatMin").text == "1"
    assert record_info_reference.find("repeatMax").text == "1"


def test_update_data_divider(record_node):
    assert common_utils.update_data_divider(record_node.xml_content, "something_else")
    divider_value = record_node.xml_content.find(".//recordInfo/dataDivider/linkedRecordId")
    assert divider_value.text == "something_else"


def test_update_child_references_on_node_tree(create_node_tree):
    node_map = create_node_tree

    for node in node_map.values():
        linked_id = ET.SubElement(node.xml_content, "linkedRecordId")
        linked_id.text = node.record_id

    id_mapping = {
        "A": "X",
        "C": "Y",
        "E": "Z"
    }

    for node in node_map.values():
        common_utils.update_child_references(node.xml_content, id_mapping)

    for record_id, node in node_map.items():
        linked_id_text = node.xml_content.find("linkedRecordId").text
        if record_id in id_mapping:
            assert linked_id_text == id_mapping[record_id]
        else:
            assert linked_id_text == record_id


def test_create_new_id_with_prefix(record_node):
    original_id = f"{common_utils._type_prefix}existing_id"
    record_node.record_id = original_id
    global_id_mapping = {}

    new_id = common_utils.create_new_id_and_update_mapping(global_id_mapping, record_node)

    assert new_id == record_node.record_id
    assert record_node.new_record_id == record_node.record_id
    assert global_id_mapping[original_id] == record_node.record_id


def test_create_new_id_without_prefix(record_node):
    original_id = "original_id"
    record_node.record_id = original_id
    global_id_mapping = {}

    new_id = common_utils.create_new_id_and_update_mapping(global_id_mapping, record_node)

    updated_prefixed_id = f"{common_utils._type_prefix}{original_id}"
    assert new_id == updated_prefixed_id
    assert record_node.new_record_id == updated_prefixed_id
    assert global_id_mapping[original_id] == updated_prefixed_id


def test_create_new_id_for_data_quality(record_node):
    name_in_data = record_node.xml_content.find(".//metadata/nameInData")
    name_in_data.text = "dataQuality"

    original_id = "existing_id"
    record_node.record_id = original_id
    global_id_mapping = {}

    new_id = common_utils.create_new_id_and_update_mapping(global_id_mapping, record_node)

    assert new_id == f"{common_utils._type_prefix}dataQualityCollectionVar"
    assert record_node.new_record_id == f"{common_utils._type_prefix}dataQualityCollectionVar"
    assert global_id_mapping[original_id] == f"{common_utils._type_prefix}dataQualityCollectionVar"


def test_update_record_id_in_xml(record_node):
    common_utils.update_record_id_in_xml(record_node.xml_content, "over9000")
    assert record_node.xml_content.find(".//recordInfo/id").text == "over9000"


def test_remove_action_links(record_node):
    common_utils.remove_action_links(record_node.xml_content)
    urls = record_node.xml_content.findall(".//actionLinks")
    assert not urls


def test_parse_record_from_xml(sample_xml):
    node = common_utils.parse_record_from_xml(sample_xml, "http://some_url")
    assert node.record_id == "__test_prefix_divaTextNewGroup"
    assert node.record_type == "metadata"
    assert node.url == "http://some_url"


def test_fetch_record_as_xml(monkeypatch, sample_xml):
    xml = common_utils.fetch_record_as_xml("http://someurl/record")
    assert sample_xml in xml


def test_clean_and_unwrap_xml(record_node):
    content = common_utils.unwrap_and_clean_xml_for_create(record_node.xml_content)
    assert content.tag == "metadata"
    common_utils.remove_unwanted_elements_for_creation(content)
    for tag in ["type", "createdBy", "tsCreated", "updated"]:
        assert content.find(tag) is None


def test_to_xml_bytes(record_node):
    xml_bytes = common_utils.to_xml_bytes(record_node.xml_content)
    assert xml_bytes.startswith(b"<?xml")


def test_collect_child_urls(record_node):
    urls = common_utils.collect_child_urls(record_node, "http://root_url", "http://some_url")
    assert urls == ['http://HOSTURL/recordInfoNewDivaTextGroup', 'http://HOSTURL/textPartSvGroup',
                    'http://HOSTURL/textPartEnGroup']


def test_collect_child_urls_with_root_url(record_node, mock_top_level):
    urls = common_utils.collect_child_urls(record_node, "http://root_url", "http://root_url")
    assert urls == ["http://HOSTURL/newGroupChild", "http://HOSTURL/updateGroupChild"]


def test_find_top_level_children(record_node, mock_top_level):
    urls = common_utils.find_top_level_children(record_node.xml_content)
    assert urls == ["http://HOSTURL/newGroupChild", "http://HOSTURL/updateGroupChild"]


def test_find_child_urls(record_node):
    urls = common_utils.find_child_urls(record_node.xml_content)
    assert urls == ['http://HOSTURL/recordInfoNewDivaTextGroup', 'http://HOSTURL/textPartSvGroup',
                    'http://HOSTURL/textPartEnGroup']


def test_get_validation_types_for_record_type(init_utils):
    results = common_utils.get_validation_types_for_record_type()
    assert results == ["valType1", "valType2"]


def test_get_ids_for_record_type_matching_prefix(init_utils):
    results = common_utils.get_ids_for_record_type_matching_prefix("presentation")
    assert results == ["__test_prefix_pres1", "__test_prefix_pres2"]


def test_break_dependency_to_top_groups(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")

    metadata_id = ET.SubElement(record_info, "newMetadataId")
    linked_record_id = ET.SubElement(metadata_id, "linkedRecordId")
    linked_record_id.text = f"{common_utils._type_prefix}_wow_a_prefix"

    common_utils.break_dependency_to_top_groups(record_node.xml_content)

    linked_record_id = record_node.xml_content.find(".//newMetadataId/linkedRecordId")
    assert not linked_record_id.text.startswith(common_utils._type_prefix)
    assert linked_record_id.text.endswith("_wow_a_prefix")


def test_update_dependency_to_top_groups(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")

    metadata_id = ET.SubElement(record_info, "newMetadataId")
    linked_record_id = ET.SubElement(metadata_id, "linkedRecordId")
    linked_record_id.text = "wow_a_prefix"

    assert common_utils.link_dependency_to_top_groups(record_node.xml_content)

    linked_record_id = record_node.xml_content.find(".//newMetadataId/linkedRecordId")
    assert linked_record_id.text.startswith(common_utils._type_prefix)
    assert linked_record_id.text.endswith("_wow_a_prefix")


def test_update_dependency_to_top_groups_no_doubles(record_node):
    record_info = record_node.xml_content.find(".//recordInfo")

    metadata_id = ET.SubElement(record_info, "newMetadataId")
    linked_record_id = ET.SubElement(metadata_id, "linkedRecordId")
    linked_record_id.text = f"{common_utils._type_prefix}wow_a_prefix"

    assert not common_utils.update_prefix_of_value_of_xpath_using_find(record_node.xml_content,
                                                                       ".//newMetadataId/linkedRecordId")
    linked_record_id = record_node.xml_content.find(".//newMetadataId/linkedRecordId")
    assert not linked_record_id.text.startswith(f"{common_utils._type_prefix}{common_utils._type_prefix}")
    assert linked_record_id.text == f"{common_utils._type_prefix}wow_a_prefix"


def test_possibly_set_to_not_create_presentations(record_node):
    common_utils.possibly_set_to_not_create_presentations(record_node)
    assert record_node.xml_content.findall(".//excludePGroupCreation")


def test_possibly_set_to_not_create_presentations_not_group(record_node):
    xml = """
    <record>
        <metadata>
            <nameInData>dataQuality</nameInData>
            <finalValue>cora2026</finalValue>
        </metadata>
    </record>
    """
    record = ET.fromstring(xml)
    record_node.xml_content = record
    common_utils.possibly_set_to_not_create_presentations(record_node)
    assert not record_node.xml_content.findall(".//excludePGroupCreation")


def test_try_to_create_record(record_node):
    errors = []
    assert common_utils.try_to_create_record(record_node, record_node.xml_content, errors)


def test_try_to_create_record_not_201(record_node):
    errors = []
    record_node.new_record_id = "some_new_id"
    record_node.record_type = "return400"
    assert not common_utils.try_to_create_record(record_node, record_node.xml_content, errors)
    assert "Failed to save some_new_id (400 - failed to post)" in errors


def test_try_to_create_record_throws_exception(record_node):
    errors = []
    record_node.new_record_id = "some_new_id"
    record_node.record_type = "throw_exception"
    assert not common_utils.try_to_create_record(record_node, record_node.xml_content, errors)
    assert "Error saving some_new_id: threw exception" in errors


def test_try_to_update_record(record_node):
    errors = []
    assert common_utils.try_to_update_record(record_node, errors)


def test_prepare_and_delete_record(record_node):
    errors = []
    record_node.record_id = f"{common_utils._type_prefix}_record_id"
    assert common_utils.prepare_and_delete_record(record_node, errors)


def test_prepare_and_delete_record_not_200(record_node):
    errors = []
    record_node.record_id = f"{common_utils._type_prefix}_not200"
    assert not common_utils.prepare_and_delete_record(record_node, errors)
    assert "Failed to delete record: http://baseUrl/validationType/__test_prefix__not200" in errors


def test_prepare_and_delete_record_not_matching_prefix(record_node):
    errors = []
    assert not common_utils.prepare_and_delete_record(record_node, errors)
    assert ("Tried to delete a record that probably wasn't supposed to be deleted... "
            "http://baseUrl/validationType/divaTextNewGroup") in errors


def test_prepare_and_delete_record_throws_exception(record_node):
    errors = []
    record_node.record_id = f"{common_utils._type_prefix}_throw_exception"
    assert not common_utils.prepare_and_delete_record(record_node, errors)
    assert "Error saving http://baseUrl/validationType/__test_prefix__throw_exception: some exception" in errors
