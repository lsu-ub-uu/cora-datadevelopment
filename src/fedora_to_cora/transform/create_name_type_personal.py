import xml.etree.ElementTree as ET
from common.common_data import create_record_link
from common.xml_utils import create_group, create_text
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


def create_thesis_advisor(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
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


def create_opponents(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
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


def create_degree_supervisor(
    source_record: ET.Element, context: Context
) -> list[ET.Element | None]:
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
) -> ET.Element | None:
    """
    Create a cora person element from a classic person element.
    """
    # TODO Handle linked person

    return create_group(
        "name",
        type="personal",
        otherType=otherType,
        repeatId=str(repeatId),
        children=[
            create_text("namePart", type="family", value=person.findtext("./lastName")),
            create_text("namePart", type="given", value=person.findtext("./firstName")),
            _create_date_part(person),
            _create_role(role_terms, author_only),
            _create_name_identifier_local_id(
                _create_name_identifier_local_id(person.find("./localId"))
            ),
            _create_name_identifier_orcid(
                person.find("./identifiers/entry/personIdentifier/value")
            ),
            _create_affiliations(person, context),
        ],
    )


def _create_date_part(person: ET.Element) -> ET.Element | None:
    birth_year = person.findtext("./birthYear")
    death_year = person.findtext("./deathYear")

    has_birth_year = birth_year is not None and birth_year.strip() != ""
    has_death_year = death_year is not None and death_year.strip() != ""

    if not has_birth_year and not has_death_year:
        return None

    date_text = ""

    if has_birth_year and not has_death_year:
        date_text = birth_year
    elif not has_birth_year and has_death_year:
        date_text = f"-{death_year}"
    else:
        date_text = f"{birth_year}-{death_year}"

    return create_text("namePart", type="date", value=date_text)


def _create_role(role_terms: list[str], author_only: bool) -> ET.Element | None:
    return create_group(
        "role",
        children=[
            create_text(
                "roleTerm",
                value=role_term,
                repeatId=str(i) if not author_only else None,
            )
            for i, role_term in enumerate(role_terms)
        ],
    )


def _create_affiliations(person: ET.Element, context: Context) -> list[ET.Element]:
    repeat_id = 0
    affiliations = []

    for organisation in person.findall("./organisations/organisation"):
        affiliations.append(create_affiliation(organisation, repeat_id, context))
        repeat_id += 1

    research_group = person.findtext("./researchGroup")
    if research_group:
        affiliations.append(
            _create_affiliation_from_research_group(research_group, repeat_id)
        )

    return affiliations


def create_affiliation(
    organisation: ET.Element, repeat_id: int, context: Context
) -> ET.Element | None:
    controlled = organisation.find("./controlled")
    if controlled is not None and controlled.text == "true":
        return create_affiliation_for_controlled_organisation(
            organisation, repeat_id, context
        )
    else:
        return create_affiliation_for_uncontrolled_organisation(organisation, repeat_id)


def create_affiliation_for_controlled_organisation(
    organisation: ET.Element, repeat_id: int, context: Context
) -> ET.Element | None:
    """
    Create an affiliation element for a controlled organisation.
    """

    organisation_id = organisation.find("./organisationId")

    assert organisation_id is not None and organisation_id.text

    return create_group(
        "affiliation",
        repeatId=str(repeat_id),
        children=[
            create_record_link(
                "organisation",
                "diva-organisation",
                get_cora_id_by_old_id(
                    organisation_id.text,
                    record_type="diva-organisation",
                    context=context,
                ),
            )
        ],
    )


def create_affiliation_for_uncontrolled_organisation(
    organisation: ET.Element, repeat_id: int
):
    """
    Create an affiliation element for an uncontrolled organisation.
    """
    return create_group(
        "affiliation",
        repeatId=str(repeat_id),
        children=[
            create_text(
                "namePart",
                value=organisation.findtext("./organisationNameUncontrolled"),
            )
        ],
    )


def _create_affiliation_from_research_group(
    research_group: str, repeat_id: int
) -> ET.Element | None:
    return create_group(
        "affiliation",
        repeatId=str(repeat_id),
        children=[
            create_text("namePart", value=research_group),
            create_text("description", value="researchGroup"),
        ],
    )


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


def _create_name_identifier_orcid(orcid: ET.Element | None):
    if orcid is None:
        return None
    return create_text("nameIdentifier", type="orcid", value=orcid.text)


def _create_name_identifier_local_id(local_id: ET.Element | None):
    if local_id is None:
        return None

    return create_text("nameIdentifier", type="localId", value=local_id.text)
