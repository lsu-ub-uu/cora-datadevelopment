import xml.etree.ElementTree as ET
from cora.get_organisation_by_old_id import get_organisation_id_by_old_id
from cora.cora_config import CoraConfigProtocol


def create_name_type_personals(
    source_record: ET.Element, config: CoraConfigProtocol
) -> list[ET.Element]:
    """
    Create a list of person names from all roles, merging them and ensuring unique repeatId.
    """

    role_terms_by_selector = [
        (".//authors/person", "aut"),
        (".//editors/person", "edt"),
        (".//examiners/person", "dgs"),
        (".//supervisors/person", "ths"),
        (".//opponents/person", "opn"),
    ]

    name_type_personals = []
    repeat_id = 0

    for selector, role_term in role_terms_by_selector:
        persons = source_record.findall(selector)
        for person in persons:
            if person is not None:
                name_type_personals.append(
                    create_name_type_personal(person, [role_term], repeat_id, config)
                )
                repeat_id += 1

    for contributor in source_record.findall(".//otherContributors/contributor"):
        role_terms = [
            marc_code.text
            for marc_code in contributor.findall("./roles/role/marcCode")
            if marc_code.text
        ]
        name_type_personals.append(
            create_name_type_personal(contributor, role_terms, repeat_id, config)
        )
        repeat_id += 1

    return name_type_personals


def create_name_type_personal(
    person: ET.Element, role_terms: list[str], repeatId: int, config: CoraConfigProtocol
) -> ET.Element:
    """
    Create a nameTypePersonal element from an author element.
    """
    name_type_personal = ET.Element("name", type="personal", repeatId=str(repeatId))

    last_name = person.find("./lastName")
    if last_name is not None and last_name.text:
        ET.SubElement(name_type_personal, "namePart", type="family").text = (
            last_name.text
        )

    first_name = person.find("./firstName")
    if first_name is not None and first_name.text:
        ET.SubElement(name_type_personal, "namePart", type="given").text = (
            first_name.text
        )

    role = ET.SubElement(name_type_personal, "role")
    for i, role_term in enumerate(role_terms):
        ET.SubElement(role, "roleTerm", type="code", repeatId=str(i)).text = role_term

    for i, organisation in enumerate(person.findall("./organisations/organisation")):
        name_type_personal.append(create_affiliation(organisation, i, config))

    return name_type_personal


def create_affiliation(
    organisation: ET.Element, repeat_id: int, config: CoraConfigProtocol
) -> ET.Element:
    controlled = organisation.find("./controlled")
    if controlled is not None and controlled.text == "true":
        return create_affiliation_for_controlled_organisation(
            organisation, repeat_id, config
        )
    else:
        return create_affiliation_for_uncontrolled_organisation(organisation, repeat_id)


def create_affiliation_for_controlled_organisation(
    organisation: ET.Element, repeat_id: int, config: CoraConfigProtocol
) -> ET.Element:
    """
    Create an affiliation element for a controlled organisation.
    """

    affiliation = ET.Element("affiliation", repeatId=str(repeat_id))
    organisation_id = organisation.find("./organisationId")

    assert organisation_id is not None and organisation_id.text

    cora_id = get_organisation_id_by_old_id(
        organisation_id.text,
        base_url=config.get_base_url(),
        auth_token=config.get_auth_token(),
    )

    organisation_link = ET.SubElement(affiliation, "organisation")
    ET.SubElement(organisation_link, "linkedRecordType").text = "diva-organisation"
    ET.SubElement(organisation_link, "linkedRecordId").text = cora_id

    return affiliation


def create_affiliation_for_uncontrolled_organisation(
    organisation: ET.Element, repeat_id: int
) -> ET.Element:
    """
    Create an affiliation element for an uncontrolled organisation.
    """
    affiliation = ET.Element("affiliation", repeatId=str(repeat_id))

    uncontrolled_name = organisation.find("./organisationNameUncontrolled")
    if uncontrolled_name is not None and uncontrolled_name.text:
        name = ET.SubElement(affiliation, "name", type="corporate")
        ET.SubElement(name, "namePart").text = uncontrolled_name.text

    return affiliation
