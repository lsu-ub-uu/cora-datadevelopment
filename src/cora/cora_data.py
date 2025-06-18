
def findChildWithNameInData(childrenList, nameInData):
    for child in childrenList:
        childNameInData = child['name']
        if childNameInData == nameInData:
            return child
    return None
    

def getValueWithNameInData(specificChild):
    if specificChild is not None:
        childValue = specificChild['value']
        return childValue
    return None


def getFirstAtomicValueWithNameInData(childrenList, nameInData):
    specificChild = findChildWithNameInData(childrenList, nameInData)
    childValue = getValueWithNameInData(specificChild)
    return childValue


def appendValueToList(childValue, element, list):
    if childValue is not None:
        list.append(element)

def getOrganisationNameValueWithNameInData(childrenList, nameInData): # borde kunna vara samma som nedan
    specificChild = findChildWithNameInData(childrenList, nameInData)
    specificChildsChildren = findChildWithNameInData(specificChild['children'], 'name')
    return specificChildsChildren['value']

def getLinkedRecordIdWithNameInData(dataChildren, nameInData): # borde kunna vara samma som ovan
    linkedChild = findChildWithNameInData(dataChildren, nameInData) 
    linkedRecordId = findChildWithNameInData(linkedChild['children'], 'linkedRecordId')
    return linkedRecordId['value']

def getValidationTypeLink(recordInfoChildren):
    validationType = getLinkedRecordIdWithNameInData(recordInfoChildren, 'type')
    # newValidationType = checkValidationTypeLinkAndGetNewValue(validationType)
    return validationType

def getParentEarlierLinks(recordChildren, typeOfOrganisationLink): # BYT UT RECORDCHILDREN TILL RESPONSE_RECORD
    linkedId = []
    for organisationLink in recordChildren:
        childNameInData = organisationLink['name']
        if childNameInData == typeOfOrganisationLink:
            organisationLinkValue = findChildWithNameInData(organisationLink['children'], 'organisationLink') 
            linkedRecordId = findChildWithNameInData(organisationLinkValue['children'], 'linkedRecordId')
            linkedId.append(linkedRecordId['value'])
    return linkedId