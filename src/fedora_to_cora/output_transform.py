import xml.etree.ElementTree as ET
from cora.context import Context
from common.xml_utils import append_if_value

from fedora_to_cora.transform.create_date_other_type_patent import (
    create_date_other_type_patent,
)
from fedora_to_cora.transform.create_note_type_publication_status import (
    create_note_type_publication_status,
)
from fedora_to_cora.transform.create_genre_type_subcategory import (
    create_genre_type_subcategory,
)
from fedora_to_cora.transform.create_admin_info import create_admin_info
from fedora_to_cora.transform.create_language import create_language
from fedora_to_cora.transform.create_record_info import create_record_info
from fedora_to_cora.transform.create_genre_type_content_type import (
    create_genre_type_content_type,
)
from fedora_to_cora.transform.create_subject_authority_diva import (
    create_subject_authority_diva,
)
from fedora_to_cora.transform.create_title_info import (
    create_title_info,
    create_title_info_type_alternative,
)
from fedora_to_cora.transform.create_subject import create_subjects
from fedora_to_cora.transform.create_artistic_work import create_artistic_work
from fedora_to_cora.transform.create_genre_type_output_type import (
    create_genre_type_output_type,
)
from fedora_to_cora.transform.create_name_type_personal import (
    create_examiners,
    create_name_type_personals,
    create_opponents,
    create_supervisors,
)
from fedora_to_cora.transform.create_abstracts import create_abstracts

from fedora_to_cora.transform.create_type_of_resource import create_type_of_resource
from fedora_to_cora.transform.degree_project.create_academic_semester import (
    create_academic_semester,
)
from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
    create_identifier_se_libr,
)
from fedora_to_cora.transform.related_items.create_conference import (
    create_related_item_type_conference,
)
from fedora_to_cora.transform.identifiers.create_isbn import create_identifier_type_isbn
from fedora_to_cora.transform.create_origin_info import create_origin_info
from fedora_to_cora.transform.create_extent import create_extent
from fedora_to_cora.transform.create_classification_authority_ssif import (
    create_classification_authority_ssif,
)
from fedora_to_cora.transform.identifiers.create_identifier import create_identifier
from fedora_to_cora.transform.create_note import create_note
from fedora_to_cora.transform.create_location import create_locations
from fedora_to_cora.transform.create_subject_authority_sdg import (
    create_subject_authority_sdg,
)
from fedora_to_cora.transform.related_items.create_journal import (
    create_related_item_type_journal,
)
from fedora_to_cora.transform.related_items.create_series import (
    create_related_item_type_series,
)

from fedora_to_cora.transform.degree_project.create_student_degree import (
    create_student_degrees,
)
from fedora_to_cora.transform.degree_project.create_external_collaboration import (
    create_external_collaboration,
)
from fedora_to_cora.transform.create_degree_granting_institution import (
    create_degree_granting_institution,
)

from fedora_to_cora.transform.related_items.create_project import (
    create_related_item_type_project,
)
from fedora_to_cora.transform.thesis.create_defence_or_presentation import (
    create_defence_or_presentation,
)
from fedora_to_cora.transform.artistic_output.create_artistic_output import (
    create_physical_desctiption,
    create_duration,
    create_size,
    create_techniques,
    create_materials,
    create_types,
)


def transform_to_cora_output(source_record: ET.Element, context: Context) -> ET.Element:
    target_record = ET.Element("output")

    # create student_degree

    append_if_value(target_record, create_record_info(source_record))

    ET.SubElement(target_record, "dataQuality").text = "2026"

    append_if_value(target_record, create_genre_type_content_type(source_record))

    append_if_value(target_record, create_title_info(source_record))

    append_if_value(target_record, create_subjects(source_record))

    append_if_value(target_record, create_date_other_type_patent(source_record))

    append_if_value(target_record, create_origin_info(source_record, context))

    append_if_value(target_record, create_extent(source_record))

    append_if_value(target_record, create_classification_authority_ssif(source_record))

    append_if_value(
        target_record, create_subject_authority_diva(source_record, context)
    )

    append_if_value(target_record, create_genre_type_output_type(source_record))

    append_if_value(target_record, create_genre_type_subcategory(source_record))

    append_if_value(target_record, create_language(source_record))

    append_if_value(target_record, create_note_type_publication_status(source_record))

    append_if_value(target_record, create_artistic_work(source_record))

    append_if_value(target_record, create_title_info_type_alternative(source_record))

    # Does not handle linked persons yet
    append_if_value(target_record, create_name_type_personals(source_record, context))

    append_if_value(
        target_record,
        create_note(
            source_record, type="creatorCount", source_selector="./noOfContributors"
        ),
    )

    append_if_value(target_record, create_type_of_resource(source_record))

    append_if_value(target_record, create_types(source_record))

    append_if_value(target_record, create_materials(source_record))

    append_if_value(target_record, create_techniques(source_record))

    append_if_value(target_record, create_size(source_record))

    append_if_value(target_record, create_duration(source_record))

    append_if_value(target_record, create_abstracts(source_record))

    append_if_value(target_record, create_admin_info(source_record))

    append_if_value(
        target_record,
        create_subject_authority_sdg(source_record),
    )

    append_if_value(target_record, create_identifier_type_isbn(source_record))

    append_if_value(
        target_record,
        create_identifier(source_record, type="isrn"),
    )

    append_if_value(
        target_record,
        create_identifier(source_record, type="archiveNumber"),
    )

    append_if_value(
        target_record,
        create_identifier(source_record, type="localId"),
    )

    append_if_value(
        target_record,
        create_identifier(source_record, type="pmid"),
    )

    append_if_value(
        target_record,
        create_identifier(source_record, type="wos", source_selector="./isi"),
    )

    append_if_value(
        target_record,
        create_identifier(source_record, type="scopus", source_selector="./scopusId"),
    )

    append_if_value(target_record, create_identifier_se_libr(source_record))
    append_if_value(target_record, create_identifier_doi(source_record))

    append_if_value(
        target_record,
        create_identifier(source_record, type="patentNumber"),
    )

    append_if_value(
        target_record,
        create_locations(source_record),
    )

    append_if_value(
        target_record,
        create_note(source_record, type="external", source_selector="./note"),
    )

    append_if_value(
        target_record,
        create_related_item_type_series(source_record, context),
    )
    append_if_value(target_record, create_related_item_type_conference(source_record))
    append_if_value(target_record, create_student_degrees(source_record, context))

    append_if_value(
        target_record,
        create_external_collaboration(source_record),
    )

    append_if_value(
        target_record,
        create_degree_granting_institution(source_record, context),
    )

    append_if_value(target_record, create_supervisors(source_record, context))

    append_if_value(target_record, create_examiners(source_record, context))

    append_if_value(target_record, create_opponents(source_record, context))

    append_if_value(target_record, create_academic_semester(source_record))

    append_if_value(target_record, create_external_collaboration(source_record))

    append_if_value(target_record, create_student_degrees(source_record, context))

    append_if_value(target_record, create_defence_or_presentation(source_record))

    append_if_value(
        target_record, create_related_item_type_journal(source_record, context)
    )

    append_if_value(
        target_record, create_related_item_type_project(source_record, context)
    )

    return target_record


# create_type_of_resource
