import xml.etree.ElementTree as ET
from cora.cora_config import CoraConfigProtocol

from fedora_to_cora import (
    create_language,
    create_record_info,
    create_genre_type_content_type,
    create_title_info,
    create_subject,
    create_artistic_work,
    create_genre_type_output_type,
    create_title_info_type_alternative,
    create_name_type_personals,
    create_note_type_creator_count,
)


def transform_to_cora_output(
    source_record: ET.Element, cora_config: CoraConfigProtocol
) -> ET.Element:
    target_record = ET.Element("output")

    def _append(child: ET.Element | None):
        if child is not None:
            target_record.append(child)

    def _append_all(children: list[ET.Element]):
        for child in children:
            _append(child)

    # --- Behövs för Sammlingsverk --- #

    # recordInfo
    ## validationType <- publicationTypeId
    ## permissionUnit <- domain
    ## oldId <- pid
    ## visibility <- administrativeInfo/updaters/userInformation/userAction
    _append(create_record_info(source_record))

    # genre type="contentType" <- contentTypeCode
    _append(create_genre_type_content_type(source_record))

    # titleInfo type="main" <- originalPublicationTitle
    _append(create_title_info(source_record))

    # subject <- keyWords
    _append(create_subject(source_record))

    # genre type="outputType" (valideringstyp) <- publicationType via get_validation_type_by_publication_typ
    _append(create_genre_type_output_type(source_record))

    # language <- originalPublicationTitle/language
    _append(create_language(source_record))

    # artisticWork type="outputType" <- artistic work
    _append(create_artistic_work(source_record))
    # titleInfo type="alternative"  <- alternativePublicationTitles
    _append_all(create_title_info_type_alternative(source_record))

    # name type="personal"
    _append_all(create_name_type_personals(source_record, cora_config))

    # name type="corporate" <- skipped
    _append(create_note_type_creator_count(source_record))
    # abstract <- abstracts
    # originInfo
    ## dateIssued
    ## copyrightDate
    ## dateOther type="online"
    ## agent
    ## place
    ## edition
    # extent <- Verkets fysiska omfattning
    # classification authority="ssif" <- nationalCategories
    # subject authority="diva" <- researchSubjects
    # subject authority="sdg" <- sustainableDevelopments / behöver extra jobb

    # identifier type="isbn"
    # identifier type="isrn"
    # identifier type="doi"
    # identifier type="ismn"
    # identifier type="archiveNumber"
    # identifier type="openAlex"
    # identifier type="se-libr"
    # identifier type="localId"

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
    # identifier type="pmid"
    # identifier type="wos"
    # identifier type="scopus"
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
