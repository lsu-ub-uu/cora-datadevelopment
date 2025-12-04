import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from common.xml_utils import append_if_value
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id
from cora.context import Context
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)


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
                        author_only=_is_author_only_type(source_record),
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
            otherType="thesisAdvisor",
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
            otherType="opponent",
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
            otherType="degreeSupervisor",
        )
        for i, examiner in enumerate(examiners)
    ]


def create_name_type_personal(
    person: ET.Element,
    role_terms: list[str],
    repeatId: int,
    context: Context,
    author_only: bool = False,
    otherType: str | None = None,
) -> ET.Element:
    """
    Create a cora person element from a classic person element.
    """
    name_type_personal = ET.Element("name", type="personal", repeatId=str(repeatId))

    if otherType is not None:
        name_type_personal.set("otherType", otherType)

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

    append_if_value(name_type_personal, _create_date_part(person))

    append_if_value(name_type_personal, _create_role(role_terms, author_only))

    local_id = person.find("./localId")
    if local_id is not None and local_id.text:
        name_type_personal.append(_create_name_identifier_local_id(local_id))

    orcid = person.find("./identifiers/entry/personIdentifier/value")
    if orcid is not None and orcid.text:
        name_type_personal.append(_create_name_identifier_orcid(orcid))

    for i, organisation in enumerate(person.findall("./organisations/organisation")):
        name_type_personal.append(create_affiliation(organisation, i, context))

    return name_type_personal


def _create_date_part(person: ET.Element) -> ET.Element | None:
    birth_year = person.findtext("./birthYear")
    death_year = person.findtext("./deathYear")

    has_birth_year = birth_year is not None and birth_year.strip() != ""
    has_death_year = death_year is not None and death_year.strip() != ""

    if not has_birth_year and not has_death_year:
        return None

    date_part = ET.Element("namePart", type="date")

    if has_birth_year and not has_death_year:
        date_part.text = birth_year
    elif not has_birth_year and has_death_year:
        date_part.text = f"-{death_year}"
    else:
        date_part.text = f"{birth_year}-{death_year}"

    return date_part


def _create_role(role_terms: list[str], author_only: bool) -> ET.Element:
    role = ET.Element("role")
    for i, role_term in enumerate(role_terms):
        role_term_el = ET.SubElement(role, "roleTerm")
        role_term_el.text = role_term
        if not author_only:
            role_term_el.set("repeatId", str(i))
    return role


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

    affiliation = ET.Element("affiliation", repeatId=str(repeat_id))
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
    affiliation = ET.Element("affiliation", repeatId=str(repeat_id))

    uncontrolled_name = organisation.find("./organisationNameUncontrolled")
    if uncontrolled_name is not None and uncontrolled_name.text:
        ET.SubElement(affiliation, "namePart").text = uncontrolled_name.text

    return affiliation


def _is_author_only_type(source_record: ET.Element) -> bool:
    """
    Check if the validation type only allows a single role (author)
    """

    author_only_validation_types = {
        "publication_doctoral-thesis-compilation",
        "publication_licentiate-thesis-monograph",
        "diva_degree-project",
        "conference_other",
        "conference_poster",
        "conference_paper",
        "publication_preprint",
        "publication_licentiate-thesis-compilation",
        "publication_licentiate-thesis-monograph",
    }
    validation_type = get_validation_type_from_fedora_record(source_record)

    return validation_type in author_only_validation_types


def _create_name_identifier_orcid(orcid: ET.Element) -> ET.Element:
    identifier = ET.Element("nameIdentifier", type="orcid")
    if orcid.text:
        identifier.text = orcid.text
    return identifier


def _create_name_identifier_local_id(local_id: ET.Element) -> ET.Element:
    identifier = ET.Element("nameIdentifier", type="localId")
    if local_id.text:
        identifier.text = local_id.text
    return identifier
