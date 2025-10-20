import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from cora.context import Context


def create_name_type_personals(
    source_record: ET.Element, context: Context
) -> list[ET.Element]:
    """
    Create a list of person names from all roles, merging them and ensuring unique repeatId.
    """

    role_terms_by_selector = [
        (".//authors/person", "aut"),
        (".//editors/person", "edt"),
    ]

    name_type_personals = []
    repeat_id = 0

    for selector, role_term in role_terms_by_selector:
        persons = source_record.findall(selector)
        for person in persons:
            if person is not None:
                name_type_personals.append(
                    create_name_type_personal(
                        person,
                        [role_term],
                        repeat_id,
                        context,
                        author_only=is_author_only_type(source_record),
                    )
                )
                repeat_id += 1

    for contributor in source_record.findall(".//otherContributors/contributor"):
        role_terms = [
            marc_code.text
            for marc_code in contributor.findall("./roles/role/marcCode")
            if marc_code.text
        ]
        name_type_personals.append(
            create_name_type_personal(contributor, role_terms, repeat_id, context)
        )
        repeat_id += 1

    return name_type_personals


def create_supervisors(source_record: ET.Element, context: Context) -> list[ET.Element]:
    supervisors = source_record.findall(".//supervisors/person")
    return [
        create_name_type_personal(
            supervisor,
            ["ths"],
            i,
            context,
            tagName="supervisor",
        )
        for i, supervisor in enumerate(supervisors)
    ]


def create_opponents(source_record: ET.Element, context: Context) -> list[ET.Element]:
    opponents = source_record.findall(".//opponents/person")
    return [
        create_name_type_personal(
            opponent,
            ["opn"],
            i,
            context,
            tagName="opponent",
        )
        for i, opponent in enumerate(opponents)
    ]


def create_examiners(source_record: ET.Element, context: Context) -> list[ET.Element]:
    examiners = source_record.findall(".//examiners/person")
    return [
        create_name_type_personal(
            examiner,
            ["dgs"],
            i,
            context,
            tagName="examiner",
        )
        for i, examiner in enumerate(examiners)
    ]


def create_name_type_personal(
    person: ET.Element,
    role_terms: list[str],
    repeatId: int,
    context: Context,
    author_only: bool = False,
    tagName: str = "name",
) -> ET.Element:
    """
    Create a cora person element from a classic person element.
    """
    name_type_personal = ET.Element(tagName, type="personal", repeatId=str(repeatId))

    # TODO Handle linked person

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
        role_term_el = ET.SubElement(role, "roleTerm")
        role_term_el.text = role_term
        if not author_only:
            role_term_el.set("repeatId", str(i))

    for i, organisation in enumerate(person.findall("./organisations/organisation")):
        name_type_personal.append(create_affiliation(organisation, i, context))

    return name_type_personal


def create_affiliation(
    organisation: ET.Element, repeat_id: int, context: Context
) -> ET.Element:
    controlled = organisation.find("./controlled")
    if controlled is not None and controlled.text == "true":
        return create_affiliation_for_controlled_organisation(
            organisation, repeat_id, context
        )
    else:
        return create_affiliation_for_uncontrolled_organisation(organisation, repeat_id)


def create_affiliation_for_controlled_organisation(
    organisation: ET.Element, repeat_id: int, context: Context
) -> ET.Element:
    """
    Create an affiliation element for a controlled organisation.
    """

    affiliation = ET.Element("affiliation", otherType="link", repeatId=str(repeat_id))
    organisation_id = organisation.find("./organisationId")

    assert organisation_id is not None and organisation_id.text

    cora_id = get_cora_id_by_old_id(
        organisation_id.text,
        record_type="diva-organisation",
        context=context,
    )

    organisation_link = create_record_link_using_name_type_id(
        "organisation", "diva-organisation", cora_id
    )
    affiliation.append(organisation_link)

    return affiliation


def create_affiliation_for_uncontrolled_organisation(
    organisation: ET.Element, repeat_id: int
) -> ET.Element:
    """
    Create an affiliation element for an uncontrolled organisation.
    """
    affiliation = ET.Element("affiliation", otherType="text", repeatId=str(repeat_id))

    uncontrolled_name = organisation.find("./organisationNameUncontrolled")
    if uncontrolled_name is not None and uncontrolled_name.text:
        name = ET.SubElement(affiliation, "name", type="corporate")
        ET.SubElement(name, "namePart").text = uncontrolled_name.text

    return affiliation


def is_author_only_type(source_record: ET.Element) -> bool:
    """
    Check if the publication type only allows a single role (author)
    """

    author_only_types = {"53", "56", "65"}
    publication_type_id = source_record.findtext("./publicationType/publicationTypeId")
    return publication_type_id in author_only_types
