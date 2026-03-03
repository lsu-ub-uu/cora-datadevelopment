from common.xml_validate import XMLSpec, XMLValidationError, validate_xml
from common.common_data import read_source_xml

fedora_user_information_spec: XMLSpec = {
    "userId": "$ANY_TEXT$",
    "ip": "$ANY_TEXT$",
    "name": "$ANY_TEXT$",
    "date": "$ANY_TEXT$",
    "userType": "$ANY_TEXT$",
    "userAction": "$ANY_TEXT$",
}

fedora_country_spec: XMLSpec = {
    "countryCode": "$ANY_TEXT$",
    "countryNames": {
        "countryName": {
            "countryNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "countryName": "$ANY_TEXT$",
        },
    },
    "showsOnList": "$ANY_TEXT$",
}

fedora_frida_level_spec: XMLSpec = {
    "fridaLevelId": "$ANY_TEXT$",
    "fridaLevelCode": "$ANY_TEXT$",
    "fridaLevelNames": {
        "fridaLevelName": {
            "fridaLevelNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "fridaLevelName": "$ANY_TEXT$",
        }
    },
}

# Base organisation spec without circular references
fedora_organisation_spec: XMLSpec = {
    "organisationId": "$ANY_TEXT$",
    "organisationType": {
        "organisationTypeId": "$ANY_TEXT$",
        "organisationTypeCode": "$ANY_TEXT$",
        "organisationTypeNames": {
            "organisationTypeName": {
                "organisationTypeNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "organisationTypeName": "$ANY_TEXT$",
            }
        },
    },
    "organisationName": {
        "name": "$ANY_TEXT$",
        "locale": "$ANY_TEXT$",
    },
    "organisationContacts": {
        "organisationContactId": "$ANY_TEXT$",
        "organisationContactType": "$ANY_TEXT$",
        "organisationContactText": "$ANY_TEXT$",
    },
    "organisationCode": "$ANY_TEXT$",
    "organisationHomepage": "$ANY_TEXT$",
    "domain": "$ANY_TEXT$",
    "closedDate": "$ANY_TEXT$",
    "organisationNumber": "$ANY_TEXT$",
    "oldDivaDb": "$ANY_TEXT$",
    "oldDivaId": "$ANY_TEXT$",
    "oldParentId": "$ANY_TEXT$",
    "organisationAlternativeNames": {
        "organisationName": {
            "organisationNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "organisationName": "$ANY_TEXT$",
        }
    },
    "organisationAddress": {
        "addressId": "$ANY_TEXT$",
        "postbox": "$ANY_TEXT$",
        "street": "$ANY_TEXT$",
        "postnumber": "$ANY_TEXT$",
        "city": "$ANY_TEXT$",
        "country": fedora_country_spec,
    },
    "organisationPredecessorDescriptions": {
        "diva2.commons.aura.list.organisation.OrganisationPredecessorDescription": {
            "organisationPredecessorDescriptionId": "$ANY_TEXT$",
            "predecessorId": "$ANY_TEXT$",
            "description": "$ANY_TEXT$",
        }
    },
    "controlled": "$ANY_TEXT$",
    "notEligible": "$ANY_TEXT$",
    "showInPortal": "$ANY_TEXT$",
    "showInDefence": "$ANY_TEXT$",
    "topLevel": "$ANY_TEXT$",
    "organisationNameUncontrolled": "$ANY_TEXT$",
}

# Add circular references
fedora_organisation_spec["organisationParents"] = {
    "organisation": fedora_organisation_spec,
}
fedora_organisation_spec["organisationPredecessors"] = {
    "organisation": fedora_organisation_spec,
}


fedora_person_spec: XMLSpec = {
    "firstName": "$ANY_TEXT$",
    "lastName": "$ANY_TEXT$",
    "localId": "$ANY_TEXT$",
    "organisations": {
        "organisation": fedora_organisation_spec,
    },
    "email": "$ANY_TEXT$",
    "birthYear": "$ANY_TEXT$",
    "deathYear": "$ANY_TEXT$",
    "title": "$ANY_TEXT$",
    "researchGroup": "$ANY_TEXT$",
    "identifiers": {
        "entry": {
            "personIdentifierType": "$ANY_TEXT$",
            "personIdentifier": {
                "value": "$ANY_TEXT$",
                "type": "$ANY_TEXT$",
            },
        }
    },
    "authorityPid": "$ANY_TEXT$",
}


fedora_language_spec: XMLSpec = {
    "languageCode3": "$ANY_TEXT$",
    "languageCode2": "$ANY_TEXT$",
    "languageNames": {
        "languageName": {
            "languageNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "languageName": "$ANY_TEXT$",
        }
    },
    "showsOnList": "$ANY_TEXT$",
}

fedora_publication_title_spec: XMLSpec = {
    "title": "$ANY_TEXT$",
    "subTitle": "$ANY_TEXT$",
    "language": fedora_language_spec,
}

fedora_publication_type_spec: XMLSpec = {
    "publicationTypeId": "$ANY_TEXT$",
    "publicationTypeCode": "$ANY_TEXT$",
    "openUrlType": "$ANY_TEXT$",
    "publicationTypeNames": {
        "publicationTypeName": {
            "publicationTypeNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "publicationTypeName": "$ANY_TEXT$",
        }
    },
    "roles": "$ANY_TEXT$",
    "comprehensiveSummary": "$ANY_TEXT$",
    "domainAdminOnly": "$ANY_TEXT$",
    "contentTypes": "$IGNORE$",
}

fedora_content_type_spec: XMLSpec = {
    "contentTypeId": "$ANY_TEXT$",
    "contentTypeCode": "$ANY_TEXT$",
    "contentTypeNames": {
        "contentTypeName": {
            "contentTypeNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "contentTypeName": "$ANY_TEXT$",
        }
    },
    "sortOrder": "$ANY_TEXT$",
}

fedora_title_spec: XMLSpec = {
    "titleId": "$ANY_TEXT$",
    "mainTitle": "$ANY_TEXT$",
    "subTitle": "$ANY_TEXT$",
    "locale": "$ANY_TEXT$",
}

fedora_series_spec: XMLSpec = {
    "seriesId": "$ANY_TEXT$",
    "seriesTitle": fedora_title_spec,
    "seriesAlternativeTitles": {"seriesAlternativeTitle": fedora_title_spec},
    "issn": "$ANY_TEXT$",
    "eissn": "$ANY_TEXT$",
    "url": "$ANY_TEXT$",
    "keyTitle": "$ANY_TEXT$",
    "contentType": fedora_content_type_spec,
    "format": {
        "formatId": "$ANY_TEXT$",
        "formatCode": "$ANY_TEXT$",
        "formatNames": {
            "formatName": {
                "formatNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "formatName": "$ANY_TEXT$",
            }
        },
    },
    "notes": "$ANY_TEXT$",
    "subjects": "$IGNORE$",
    "publicationType": fedora_publication_type_spec,
    "organisation": fedora_organisation_spec,
    "domain": "$ANY_TEXT$",
    "closedDate": "$ANY_TEXT$",
    "controlled": "$ANY_TEXT$",
}
fedora_series_spec["relationships"] = {
    "seriesRelation": {
        "relationId": "$ANY_TEXT$",
        "relationType": {
            "relationTypeId": "$ANY_TEXT$",
            "relationTypeCode": "$ANY_TEXT$",
            "relationTypeNames": {
                "relationTypeName": {
                    "relationTypeNameId": "$ANY_TEXT$",
                    "locale": "$ANY_TEXT$",
                    "relationTypeName": "$ANY_TEXT$",
                }
            },
        },
        "relative": fedora_series_spec,
    }
}


fedora_subject_spec: XMLSpec = {
    "subjectId": "$ANY_TEXT$",
    "subjectType": {
        "subjectTypeId": "$ANY_TEXT$",
        "subjectTypeCode": "$ANY_TEXT$",
        "subjectTypeNames": {
            "subjectTypeName": {
                "subjectTypeNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "subjectTypeName": "$ANY_TEXT$",
            }
        },
    },
    "subjectNames": {
        "subjectName": {
            "subjectNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "subjectName": "$ANY_TEXT$",
        }
    },
    "subjectCode": "$ANY_TEXT$",
    "domain": "$ANY_TEXT$",
    "notEligible": "$ANY_TEXT$",
    "oldDivaDb": "$ANY_TEXT$",
    "oldDivaId": "$ANY_TEXT$",
    "organisations": {"organisation": fedora_organisation_spec},
}
fedora_subject_spec["parents"] = {"subject": fedora_subject_spec}
fedora_subject_spec["predecessors"] = {"subject": fedora_subject_spec}

fedora_funder_spec: XMLSpec = {
    "funderId": "$ANY_TEXT$",
    "funderName": {"name": "$ANY_TEXT$", "locale": "$ANY_TEXT$"},
    "organisationNumber": "$ANY_TEXT$",
    "funderAlternativeNames": {
        "diva2.commons.aura.list.funder.FunderName": {
            "funderNameId": "$ANY_TEXT$",
            "locale": "$ANY_TEXT$",
            "funderName": "$ANY_TEXT$",
        }
    },
    "doi": "$ANY_TEXT$",
}

fedora_abstract_spec: XMLSpec = {
    "language": fedora_language_spec,
    "text": "$ANY_TEXT$",
}

fedora_entry_spec: XMLSpec = {
    "language": fedora_language_spec,
    "list": {
        "string": "$ANY_TEXT$",
    },
}

fedora_student_degree_spec: XMLSpec = {
    "thesisLevel": {
        "thesisLevelId": "$ANY_TEXT$",
        "thesisLevelCode": "$ANY_TEXT$",
        "thesisLevelOldCode": "$ANY_TEXT$",
        "thesisLevelNames": {
            "thesisLevelName": {
                "thesisLevelNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "thesisLevelName": "$ANY_TEXT$",
            }
        },
        "degrees": "$IGNORE$",
        "domain": "$ANY_TEXT$",
    },
    "universityPoints": {
        "points": "$ANY_TEXT$",
        "name__sv": "$ANY_TEXT$",
        "name__en": "$ANY_TEXT$",
        "name__no": "$ANY_TEXT$",
        "hp": "$ANY_TEXT$",
    },
    "undergraduateSubject": fedora_subject_spec,
}

fedora_journal_spec: XMLSpec = {
    "journalId": "$ANY_TEXT$",
    "nordicListId": "$ANY_TEXT$",
    "journalType": {
        "journalTypeId": "$ANY_TEXT$",
        "journalTypeCode": "$ANY_TEXT$",
        "journalTypeNames": {
            "journalTypeName": {
                "journalTypeNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "journalTypeName": "$ANY_TEXT$",
            }
        },
    },
    "journalTitle": fedora_title_spec,
    "printedIssn": "$ANY_TEXT$",
    "electronicIssn": "$ANY_TEXT$",
    "url": "$ANY_TEXT$",
    "fridaLevel": fedora_frida_level_spec,
    "controlled": "$ANY_TEXT$",
    "openAccess": "$ANY_TEXT$",
    "subjects": "$IGNORE$",
    "relationships": "$IGNORE$",
}

fedora_attachment_spec: XMLSpec = {
    "mimeType": {
        "mimeTypeId": "$ANY_TEXT$",
        "mimeTypeName": "$ANY_TEXT$",
        "fileSuffix": "$ANY_TEXT$",
        "datasetOnly": "$ANY_TEXT$",
    },
    "fileLabel": {
        "fileLabelId": "$ANY_TEXT$",
        "fileLabelCode": "$ANY_TEXT$",
        "fileLabelNames": {
            "fileLabelName": {
                "fileLabelNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "fileLabelName": "$ANY_TEXT$",
            }
        },
    },
    "fileName": "$ANY_TEXT$",
    "fileSize": "$ANY_TEXT$",
    "selectedFileName": "$ANY_TEXT$",
    "path": "$ANY_TEXT$",
    "checksums": {
        "checksum": {
            "type": "$ANY_TEXT$",
            "digest": "$ANY_TEXT$",
        }
    },
    "order": "$ANY_TEXT$",
    "uploadDate": "$ANY_TEXT$",
    "asyncUpload": "false",  # Value should always be false
    "availableUntil": "$ANY_TEXT$",
    "availableFrom": "$ANY_TEXT$",
    "tempAvailableFrom": "$ANY_TEXT$",
    "deleteDate": "$ANY_TEXT$",
    "onHold": "false",  # Value should always be false
    "deleted": "$ANY_TEXT$",
    "prePrint": "$ANY_TEXT$",
    "postPrint": "$ANY_TEXT$",
    "print": "$ANY_TEXT$",
    "archiveOnly": "$ANY_TEXT$",
    "printOnDemand": "$ANY_TEXT$",
    "toBePublished": "$ANY_TEXT$",
    "toBeArchived": "$ANY_TEXT$",
    "digitized": "$ANY_TEXT$",
    "hasCoverPage": "$ANY_TEXT$",
    "coverPageConditions": "$ANY_TEXT$",
    "description": "$ANY_TEXT$",
    "secrecyInfo": {
        "secrecy": "$ANY_TEXT$",
    },
    "registrationNumber": "$ANY_TEXT$",
}


fedora_publication_xml_spec: XMLSpec = {
    "contentType": fedora_content_type_spec,
    "publicationType": fedora_publication_type_spec,
    "pid": "$ANY_TEXT$",
    "administrativeInfo": {
        "domain": "$ANY_TEXT$",
        "creatorInfo": fedora_user_information_spec,
        "updaters": {"userInformation": fedora_user_information_spec},
        "createdDate": "$ANY_TEXT$",
        "updatedDate": "$ANY_TEXT$",
        "deletedDate": "$ANY_TEXT$",
        "deleterInfo": fedora_user_information_spec,
        "fileUploadMessage": "$ANY_TEXT$",
        "importSource": "$ANY_TEXT$",
    },
    "publicationDate": "$ANY_TEXT$",
    "authors": {"person": fedora_person_spec},
    "noOfContributors": "$ANY_TEXT$",
    "originalPublicationTitle": fedora_publication_title_spec,
    "alternativePublicationTitles": {"title": fedora_publication_title_spec},
    "seriesInfos": {
        "seriesInfo": {"series": fedora_series_spec, "numberInSeries": "$ANY_TEXT$"}
    },
    "uncontrolledSeriesInfo": {
        "series": {
            "seriesAlternativeTitles": {},  # Always empty for uncontrolled series
            "issn": "$ANY_TEXT$",
            "eissn": "$ANY_TEXT$",
            "subjects": {},  # Always empty for uncontrolled series
            "relationships": {},  # Always empty for uncontrolled series
            "seriesNameUncontrolled": "$ANY_TEXT$",
            "controlled": "$ANY_TEXT$",
        },
        "numberInSeries": "$ANY_TEXT$",
    },
    "dateIssued": "$ANY_TEXT$",
    "conference": "$ANY_TEXT$",
    "pages": "$ANY_TEXT$",
    "edition": "$ANY_TEXT$",
    "volume": "$ANY_TEXT$",
    "issueNumber": "$ANY_TEXT$",
    "startPage": "$ANY_TEXT$",
    "endPage": "$ANY_TEXT$",
    "distributor": "$IGNORE$",
    "distributorAsDist": "$IGNORE$",
    "publisher": {
        "city": "$ANY_TEXT$",
        "publisherName": "$ANY_TEXT$",
        "publishingHouse": {
            "externalId": "$ANY_TEXT$",
            "publishingHouseId": "$ANY_TEXT$",
            "name": "$ANY_TEXT$",
            "nordicListId": "$ANY_TEXT$",
            "fridaLevel": fedora_frida_level_spec,
        },
    },
    "urls": {
        "url": {
            "url": "$ANY_TEXT$",
            "label": "$ANY_TEXT$",
            "openAccess": "$ANY_TEXT$",
        }
    },
    "isrn": "$ANY_TEXT$",
    "localId": "$ANY_TEXT$",
    "archiveNumber": "$ANY_TEXT$",
    "pmid": "$ANY_TEXT$",
    "isi": "$ANY_TEXT$",
    "scopusId": "$ANY_TEXT$",
    "nbn": "$ANY_TEXT$",
    "isbnNumbers": {
        "isbn": {
            "number": "$ANY_TEXT$",
            "type": "$ANY_TEXT$",
        },
    },
    "identifiers": {
        "entry": {
            "publicationIdentifierType": "$ANY_TEXT$",
            "publicationIdentifier": {
                "value": "$ANY_TEXT$",
                "type": "$ANY_TEXT$",
                "openAccess": "$ANY_TEXT$",
                "alternativeValues": {
                    "value": {
                        "content": "$ANY_TEXT$",
                    }
                },
            },
        }
    },
    "categories": {"subject": "$IGNORE$"},  # Old SVEP categories are ignored
    "nationalCategories": {"subject": fedora_subject_spec},
    "researchSubjects": {"subject": fedora_subject_spec},
    "keyWords": {"entry": fedora_entry_spec},
    "projects": {"project": {"projectName": "$ANY_TEXT$"}},
    "projectRelations": {
        "projectRelation": {
            "relation": {
                "relationId": "$ANY_TEXT$",
                "code": "$ANY_TEXT$",
                "relationName": "$ANY_TEXT$",
                "alternativeNames": {
                    "relationAlternativeName": {
                        "relationNameId": "$ANY_TEXT$",
                        "locale": "$ANY_TEXT$",
                        "relationName": "$ANY_TEXT$",
                        "helpMessage": "$ANY_TEXT$",
                    }
                },
            },
            "pid": "$ANY_TEXT$",
        }
    },
    "abstracts": {"abstract": fedora_abstract_spec},
    "defence": {
        "date": "$ANY_TEXT$",
        "language": fedora_language_spec,
        "room": {
            "name": "$ANY_TEXT$",
            "street": "$ANY_TEXT$",
            "city": "$ANY_TEXT$",
        },
        "grantingInstitution": fedora_organisation_spec,
        "externalGrantingInstitution": "$ANY_TEXT$",
    },
    "degree": {
        "degreeId": "$ANY_TEXT$",
        "degreeNames": {
            "degreeName": {
                "degreeNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "degreeName": "$ANY_TEXT$",
            }
        },
        "organisations": {"organisation": fedora_organisation_spec},
        "oldDivaDb": "$ANY_TEXT$",
        "oldDivaId": "$ANY_TEXT$",
        "domain": "$ANY_TEXT$",
        "active": "$ANY_TEXT$",
    },
    "note": "$ANY_TEXT$",
    "internalNote": "$ANY_TEXT$",
    "organisations": {"organisation": fedora_organisation_spec},
    "articleId": "$ANY_TEXT$",
    "artisticWork": "$ANY_TEXT$",
    "oai": "$ANY_TEXT$",
    "patentDate": "$ANY_TEXT$",
    "patentNumber": "$ANY_TEXT$",
    "patentOrganisation": "$ANY_TEXT$",
    "patentCountry": fedora_country_spec,
    "examiners": {
        "person": fedora_person_spec,
    },
    "supervisors": {
        "person": fedora_person_spec,
    },
    "opponents": {
        "person": fedora_person_spec,
    },
    "otherContributors": {
        "contributor": {
            **fedora_person_spec,
            "roles": {
                "role": {
                    "roleId": "$ANY_TEXT$",
                    "marcCode": "$ANY_TEXT$",
                    "roleNames": {
                        "roleName": {
                            "roleNameId": "$ANY_TEXT$",
                            "locale": "$ANY_TEXT$",
                            "roleName": "$ANY_TEXT$",
                        }
                    },
                }
            },
        }
    },
    "editors": {"person": fedora_person_spec},
    "bookTitle": {"title": "$ANY_TEXT$", "subTitle": "$ANY_TEXT$"},
    "bookEditor": "$ANY_TEXT$",
    "proceedingsTitle": {
        "title": "$ANY_TEXT$",
        "subTitle": "$ANY_TEXT$",
        # Proceedings title language is sometimes present in source data from imports, but is not used by Classic or Cora
        "language": "$IGNORE$",
    },
    "proceedingsEditor": "$ANY_TEXT$",
    "funderInfos": {
        "funderInfo": {
            "funder": fedora_funder_spec,
            "projectNumber": "$ANY_TEXT$",
        }
    },
    "geoData": {
        "description": "$ANY_TEXT$",
        "westBoundLongitude": "$ANY_TEXT$",
        "eastBoundLongitude": "$ANY_TEXT$",
        "northBoundLatitude": "$ANY_TEXT$",
        "southBoundLatitude": "$ANY_TEXT$",
        "startDate": "$ANY_TEXT$",
        "endDate": "$ANY_TEXT$",
    },
    "externalCooperation": {
        "external": "$ANY_TEXT$",
        "partners": {
            "partner": {
                "name": "$ANY_TEXT$",
            }
        },
    },
    "academicTerm": {
        "year": "$ANY_TEXT$",
        "term": "$ANY_TEXT$",
    },
    "subtype": {
        "publicationSubtypeId": "$ANY_TEXT$",
        "publicationSubtypeCode": "$ANY_TEXT$",
        "publicationSubtypeNames": {
            "publicationSubtypeName": {
                "publicationSubtypeNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "publicationSubtypeName": "$ANY_TEXT$",
            }
        },
    },
    "reviewed": "$ANY_TEXT$",
    "reviewedBefore": "$ANY_TEXT$",
    "failed": "$ANY_TEXT$",
    "hidden": "$ANY_TEXT$",
    "migrated": "$ANY_TEXT$",
    "version": "$ANY_TEXT$",
    "agreementAccepted": "$ANY_TEXT$",
    "importDuplicate": "$ANY_TEXT$",
    "registratedDuplicate": "$ANY_TEXT$",
    "publicationStatus": {
        "publicationStatusId": "$ANY_TEXT$",
        "publicationStatusNames": {
            "publicationStatusName": {
                "publicationStatusNameId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "publicationStatusName": "$ANY_TEXT$",
            }
        },
        "code": "$ANY_TEXT$",
    },
    "formatElectronic": "$ANY_TEXT$",
    "formatPrint": "$ANY_TEXT$",
    "responsibleOrganisations": {"organisation": fedora_organisation_spec},
    "canOrderOnline": "$ANY_TEXT$",
    "publicationOrder": {
        "orderProfileId": "$ANY_TEXT$",
        "orderURL": "$ANY_TEXT$",
        "orderLink": "$ANY_TEXT$",
        "validFrom": "$ANY_TEXT$",
        "parameters": {
            "parameterEditor": {
                "paramKey": "$ANY_TEXT$",
                "paramLabel": "$ANY_TEXT$",
                "paramValue": "$ANY_TEXT$",
            }
        },
    },
    "descriptions": {
        "abstract": fedora_abstract_spec,
    },
    "mediaInformation": {
        "physicalDescriptions": {"abstract": fedora_abstract_spec},
        "types": {"entry": fedora_entry_spec},
        "materials": {"entry": fedora_entry_spec},
        "techniques": {"entry": fedora_entry_spec},
        "size": "$ANY_TEXT$",
        "duration": "$ANY_TEXT$",
    },
    "publicationChannel": "$ANY_TEXT$",
    "studentDegrees": {
        "studentDegree": fedora_student_degree_spec,
    },
    "uppsokSubject": "$IGNORE$",
    "journal": fedora_journal_spec,
    "uncontrolledJournal": {
        "printedIssn": "$ANY_TEXT$",
        "electronicIssn": "$ANY_TEXT$",
        "journalNameUncontrolled": "$ANY_TEXT$",
        "controlled": "$ANY_TEXT$",
        "openAccess": "$ANY_TEXT$",
        "subjects": "$IGNORE$",
        "relationships": "$IGNORE$",
    },
    "sustainableDevelopments": {
        "sustainableDevelopment": {
            "developmentId": "$ANY_TEXT$",
            "domain": "$ANY_TEXT$",
            "name": {
                "name": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
            },
            "alternativeNames": {
                "sustainableDevelopmentName": {
                    "developmentNameId": "$ANY_TEXT$",
                    "name": {
                        "name": "$ANY_TEXT$",
                        "locale": "$ANY_TEXT$",
                    },
                }
            },
        },
    },
    "mediaType": {
        "autoId": "$ANY_TEXT$",
        "code": "$ANY_TEXT$",
        "names": {
            "mediaTypeName": {
                "autoId": "$ANY_TEXT$",
                "locale": "$ANY_TEXT$",
                "name": "$ANY_TEXT$",
            }
        },
    },
    "attachments": {
        "no-comparator": "$ANY_TEXT$",
        "attachment": fedora_attachment_spec,
    },
    # Some records have a cooperation element instead of externalCooperation.
    # If we ever find one with actual data in it, we should add it to the spec and handle it in the transformation.
    "cooperation": {
        "external": "false",
        "partner": "$EMPTY$",
    },
    # This is an alternatetive location for subtype/publicationSubtypeCode
    "publicationSubtype": "$ANY_TEXT$",
}

# Circular references for publication
fedora_publication_xml_spec["hostPublications"] = {
    "hostPublication": fedora_publication_xml_spec,
}
fedora_publication_xml_spec["partsOfPublication"] = {
    "partOfPublication": fedora_publication_xml_spec,
}
fedora_publication_xml_spec["relations"] = {
    "publicationRelation": {
        "relation": {
            "relationId": "$ANY_TEXT$",
            "code": "$ANY_TEXT$",
            "relationName": "$ANY_TEXT$",
            "alternativeNames": {
                "relationAlternativeName": {
                    "relationNameId": "$ANY_TEXT$",
                    "locale": "$ANY_TEXT$",
                    "relationName": "$ANY_TEXT$",
                    "helpMessage": "$ANY_TEXT$",
                }
            },
        },
        "relatedPid": "$ANY_TEXT$",
        "relatedPublication": fedora_publication_xml_spec,
    }
}
