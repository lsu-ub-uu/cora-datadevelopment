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


def append_value_to_list(childValue, element, list):
    if childValue is not None:
        list.append(element)


def getOrganisationNameValueWithNameInData(
    childrenList, nameInData
):  # borde kunna vara samma som nedan
    specificChild = find_child_with_name_in_data(childrenList, nameInData)
    specificChildsChildren = find_child_with_name_in_data(
        specificChild["children"], "name"
    )
    return specificChildsChildren["value"]


def get_linked_record_id_with_name_in_data(
    dataChildren, nameInData
):  # borde kunna vara samma som ovan
    linkedChild = find_child_with_name_in_data(dataChildren, nameInData)
    linkedRecordId = find_child_with_name_in_data(
        linkedChild["children"], "linkedRecordId"
    )
    return linkedRecordId["value"]


def getValidationTypeLink(recordInfoChildren):
    validationType = get_linked_record_id_with_name_in_data(recordInfoChildren, "type")
    # newValidationType = checkValidationTypeLinkAndGetNewValue(validationType)
    return validationType


def getParentEarlierLinks(
    recordChildren, typeOfOrganisationLink
):  # BYT UT RECORDCHILDREN TILL RESPONSE_RECORD
    linkedId = []
    for organisationLink in recordChildren:
        childNameInData = organisationLink["name"]
        if childNameInData == typeOfOrganisationLink:
            organisationLinkValue = find_child_with_name_in_data(
                organisationLink["children"], "organisationLink"
            )
            linkedRecordId = find_child_with_name_in_data(
                organisationLinkValue["children"], "linkedRecordId"
            )
            linkedId.append(linkedRecordId["value"])
    return linkedId
