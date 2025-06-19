import xml.etree.ElementTree as ET

from fedora_to_cora.create_record_info import create_record_info
from fedora_to_cora.create_genre_type_content_type import create_genre_type_content_type
from fedora_to_cora.create_title_info import create_title_info
from fedora_to_cora.create_subject import create_subject


def transform_to_cora_output(source_record):
    target_record = ET.Element("output")

    target_record.append(create_record_info(source_record))
    target_record.append(create_genre_type_content_type(source_record))
    target_record.append(create_title_info(source_record))
    target_record.append(create_subject(source_record))
    # genre type="outputType" (valideringstyp)
    # genre type="subcategory"
    # language
    # note type="publicationStatus"
    # artisticWork type="outputType"
    # genre type="contentType"
    # titleInfo type="alternative"
    # name type="persnal"
    # name type="corporate"
    # note type="creatorCount"
    # typeOfResource
    # type
    # material
    # technique
    # size
    # duration
    # physicalDescription
    # abstract
    # subject
    # dateOther type="patent"
    # originInfo
    # imprint
    # extent
    # classification authority="ssif"
    # subject authority="diva"
    # subject authority="sdg"
    # identifier type="isbn"
    # identifier type="isrn"
    # identifier type="ismn"
    # identifier type="patentNumber"
    # identifier type="doi"
    # identifier type="pmid"
    # identifier type="wos"
    # identifier type="scopus"
    # identifier type="openAlex"
    # identifier type="se-libr"
    # identifier type="archiveNumber"
    # identifier type="localId"
    # location
    # location displayLabel="orderLink"
    # note type="external"
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
    # relatedItem type="series"
    # relatedItem type="researchData"
    # relatedItem type="project"
    # relatedItem type="funder"
    # relatedItem type="initiative"
    # relatedItem type="retracted"
    # relatedItem type="constituent"
    # accessCondition authority="kb.se"
    # localGenericMarkup
    # admin
    # attachment

    return target_record
