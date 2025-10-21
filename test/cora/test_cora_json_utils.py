import pytest
from cora import cora_json_utils


def test_findChildWithNameInData():
    children = [
        {"name": "child1", "value": "value1"},
        {"name": "child2", "value": "value2"},
        {"name": "child3", "value": "value3"},
    ]
    assert cora_json_utils.find_child_with_name_in_data(children, "child2") == {
        "name": "child2",
        "value": "value2",
    }
    assert cora_json_utils.find_child_with_name_in_data(children, "child4") is None


def test_getValueWithNameInData():
    child = {"name": "child1", "value": "value1"}
    assert cora_json_utils.get_value_with_name_in_data(child) == "value1"
    assert cora_json_utils.get_value_with_name_in_data(None) is None


def test_getFirstAtomicValueWithNameInData():
    children = [
        {"name": "child1", "value": "value1"},
        {"name": "child2", "value": "value2"},
    ]
    assert (
        cora_json_utils.get_first_atomic_value_with_name_in_data(children, "child2")
        == "value2"
    )
    assert (
        cora_json_utils.get_first_atomic_value_with_name_in_data(children, "child3")
        is None
    )


def test_appendValueToList():
    test_list = []
    cora_json_utils.append_value_to_list("value1", "element1", test_list)
    assert test_list == ["element1"]
    cora_json_utils.append_value_to_list(None, "element2", test_list)
    assert test_list == ["element1"]


def test_getOrganisationNameValueWithNameInData():
    children = [
        {"name": "org1", "children": [{"name": "name", "value": "OrgName1"}]},
        {"name": "org2", "children": [{"name": "name", "value": "OrgName2"}]},
    ]
    assert (
        cora_json_utils.getOrganisationNameValueWithNameInData(children, "org2")
        == "OrgName2"
    )


def test_getLinkedRecordIdWithNameInData():
    children = [
        {"name": "link1", "children": [{"name": "linkedRecordId", "value": "ID1"}]},
        {"name": "link2", "children": [{"name": "linkedRecordId", "value": "ID2"}]},
    ]
    assert (
        cora_json_utils.get_linked_record_id_with_name_in_data(children, "link2")
        == "ID2"
    )


def test_getValidationTypeLink():
    recordInfoChildren = [
        {"name": "type", "children": [{"name": "linkedRecordId", "value": "TypeID"}]}
    ]
    assert cora_json_utils.getValidationTypeLink(recordInfoChildren) == "TypeID"


def test_getParentEarlierLinks():
    recordChildren = [
        {
            "name": "orgLink",
            "children": [
                {
                    "name": "organisationLink",
                    "children": [{"name": "linkedRecordId", "value": "OrgID1"}],
                }
            ],
        },
        {
            "name": "orgLink",
            "children": [
                {
                    "name": "organisationLink",
                    "children": [{"name": "linkedRecordId", "value": "OrgID2"}],
                }
            ],
        },
        {
            "name": "otherLink",
            "children": [
                {
                    "name": "organisationLink",
                    "children": [{"name": "linkedRecordId", "value": "OrgID3"}],
                }
            ],
        },
    ]
    assert cora_json_utils.getParentEarlierLinks(recordChildren, "orgLink") == [
        "OrgID1",
        "OrgID2",
    ]
