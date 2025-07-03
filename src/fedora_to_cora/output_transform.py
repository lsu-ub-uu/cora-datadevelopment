import xml.etree.ElementTree as ET
from cora.context import Context
from common.xml_utils import append_if_value

from fedora_to_cora.create_admin_info import create_admin_info
from fedora_to_cora.create_language import create_language
from fedora_to_cora.create_record_info import create_record_info
from fedora_to_cora.create_genre_type_content_type import create_genre_type_content_type
from fedora_to_cora.create_title_info import (
    create_title_info,
    create_title_info_type_alternative,
)
from fedora_to_cora.create_subject import create_subjects
from fedora_to_cora.create_artistic_work import create_artistic_work
from fedora_to_cora.create_genre_type_output_type import create_genre_type_output_type
from fedora_to_cora.create_name_type_personal import create_name_type_personals
from fedora_to_cora.create_note_type_creator_count import create_note_type_creator_count
from fedora_to_cora.create_abstracts import create_abstracts
from fedora_to_cora.create_identifier_type_isbn import create_identifier_type_isbn
from fedora_to_cora.create_identifier_type_isrn import create_identifier_type_isrn
from fedora_to_cora.create_origin_info import create_origin_info
from fedora_to_cora.create_extent import create_extent
from fedora_to_cora.create_classsification_authority_ssif import (
    create_classification_authority_ssif,
)


def transform_to_cora_output(source_record: ET.Element, context: Context) -> ET.Element:
    target_record = ET.Element("output")

    append_if_value(target_record, create_record_info(source_record))

    append_if_value(target_record, create_genre_type_content_type(source_record))

    append_if_value(target_record, create_title_info(source_record))

    append_if_value(target_record, create_subjects(source_record))

    append_if_value(target_record, create_origin_info(source_record, context))

    append_if_value(target_record, create_extent(source_record))

    append_if_value(target_record, create_classification_authority_ssif(source_record))

    append_if_value(target_record, create_genre_type_output_type(source_record))

    append_if_value(target_record, create_language(source_record))

    append_if_value(target_record, create_artistic_work(source_record))

    append_if_value(target_record, create_title_info_type_alternative(source_record))

    # Does not handle linked persons yet
    append_if_value(target_record, create_name_type_personals(source_record, context))

    append_if_value(target_record, create_note_type_creator_count(source_record))

    append_if_value(target_record, create_abstracts(source_record))

    append_if_value(target_record, create_admin_info(source_record))

    append_if_value(target_record, create_identifier_type_isbn(source_record))

    # originInfo
    ## dateIssued <- <publicationDate>
    ## copyrightDate
    ## dateOther type="online"
    ## agent
    ## place
    ## edition
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
    append_if_value(target_record, create_identifier_type_isrn(source_record))
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
