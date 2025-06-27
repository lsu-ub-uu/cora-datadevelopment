import xml.etree.ElementTree as ET
from cora.context import Context

from fedora_to_cora import (
    create_admin,
    create_language,
    create_origin_info,
    create_record_info,
    create_genre_type_content_type,
    create_title_info,
    create_subjects,
    create_artistic_work,
    create_genre_type_output_type,
    create_title_info_type_alternative,
    create_name_type_personals,
    create_note_type_creator_count,
    create_abstracts,
    create_identifier_type_isbn,
    create_identifier_type_isrn,
)


def transform_to_cora_output(source_record: ET.Element, context: Context) -> ET.Element:
    target_record = ET.Element("output")

    def _append(child: ET.Element | None):
        if child is not None and (len(child) > 0 or child.text):
            target_record.append(child)

    def _append_all(children: list[ET.Element]):
        for child in children:
            if len(child) > 0 or child.text:
                _append(child)

    _append(create_record_info(source_record))

    _append(create_genre_type_content_type(source_record))

    _append(create_title_info(source_record))

    _append_all(create_subjects(source_record))

    # work in progress
    _append(create_origin_info(source_record))

    _append(create_genre_type_output_type(source_record))

    _append(create_language(source_record))

    _append(create_artistic_work(source_record))

    _append_all(create_title_info_type_alternative(source_record))

    # Does not handle linked persons yet
    _append_all(create_name_type_personals(source_record, context))

    _append(create_note_type_creator_count(source_record))

    _append_all(create_abstracts(source_record))

    _append(create_admin(source_record))

    _append_all(create_identifier_type_isbn(source_record))

    # extent <- Verkets fysiska omfattning
    # classification authority="ssif" <- nationalCategories
    # subject authority="diva" <- researchSubjects
    # subject authority="sdg" <- sustainableDevelopments / behöver extra jobb

    # identifier type="doi"
    # identifier type="ismn"
    # identifier type="archiveNumber"
    # identifier type="openAlex"
    # identifier type="se-libr"
    # identifier type="localId"

    # identifiertype type="pmid"
    # identifiertype type="wos"
    # identifiertype type="scopus"

    # location <- urls/url
    # location displayLabel="orderLink"
    # note type="external" <- note
    # relatedItem type="series"
    # relatedItem type="researchData"
    # relatedItem type="project"
    # relatedItem type="initiative"
    # relatedItem type="retracted | constituent | thesis"
    # accessCondition authority="kb.se"
    # localGenericMarkup / ny metadata
    # admin
    ## note type="internal" <- internalNote

    # ---- Behövs för Sammlingsverk Update ----#
    # attachment

    # ---- Behövs ej för Sammlingsverk ----#
    # genre type="subcategory"
    # note type="publicationStatus"
    # genre type="contentType"
    # typeOfResource
    # type
    # material
    # technique
    # size
    # duration
    # physicalDescription
    # dateOther type="patent"
    # imprint
    # identifier type="patentNumber"
    # identifier type="isrn"
    _append(create_identifier_type_isrn(source_record))
    # academicSemester
    # studentDegree
    # externalCollaboration
    # degreeGrantingInstitution type="corporate"
    # supervisor type="personal"
    # examiner type="personal"
    # opponent type="personal"
    # presentation
    # defence
    # relatedItem type="journal"
    # relatedItem type="book"
    # relatedItem type="conferencePublication"
    # relatedItem type="conference"
    # relatedItem type="funder"
    # relatedItem type="retracted"
    # relatedItem type="constituent"

    return target_record
