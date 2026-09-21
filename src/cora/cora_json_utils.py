def find_child_with_name_in_data(childrenList, nameInData) -> dict | None:
    for child in childrenList:
        childNameInData = child["name"]
        if childNameInData == nameInData:
            return child
    return None


def find_all_children_with_name_in_data(
    childrenList: list[dict], nameInData: str
) -> list[dict]:
    matchingChildren = []
    for child in childrenList:
        childNameInData = child["name"]
        if childNameInData == nameInData:
            matchingChildren.append(child)
    return matchingChildren


def get_value_with_name_in_data(specificChild):
    if specificChild is not None:
        childValue = specificChild["value"]
        return childValue
    return None


def get_first_atomic_value_with_name_in_data(
    childrenList: list[dict], nameInData: str
) -> str | None:
    specificChild = find_child_with_name_in_data(childrenList, nameInData)
    childValue = get_value_with_name_in_data(specificChild)
    return childValue


def get_linked_record_id_with_name_in_data(dataChildren, nameInData):
    record_link = find_child_with_name_in_data(dataChildren, nameInData)
    if record_link is None:
        return None
    linked_record_id = find_child_with_name_in_data(
        record_link["children"], "linkedRecordId"
    )
    if linked_record_id is None:
        return None
    return linked_record_id["value"]
