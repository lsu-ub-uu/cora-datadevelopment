from common.xml_validate import XMLSpec, XMLValidationError, validate_xml
from common.common_data import read_source_xml

fedora_user_information_spec: XMLSpec = {
    "userId": "text",
    "ip": "text",
    "name": "text",
    "date": "text",
    "userType": "text",
    "userAction": "text",
}

fedora_country_spec: XMLSpec = {
    "countryCode": "text",
    "countryNames": {
        "countryName": {
            "countryNameId": "text",
            "locale": "text",
            "countryName": "text",
        },
    },
    "showsOnList": "text",
}

fedora_frida_level_spec: XMLSpec = {
    "fridaLevelId": "text",
    "fridaLevelCode": "text",
    "fridaLevelNames": {
        "fridaLevelName": {
            "fridaLevelNameId": "text",
            "locale": "text",
            "fridaLevelName": "text",
        }
    },
}

# Base organisation spec without circular references
fedora_organisation_spec: XMLSpec = {
    "organisationId": "text",
    "organisationType": {
        "organisationTypeId": "text",
        "organisationTypeCode": "text",
        "organisationTypeNames": {
            "organisationTypeName": {
                "organisationTypeNameId": "text",
                "locale": "text",
                "organisationTypeName": "text",
            }
        },
    },
    "organisationName": {
        "name": "text",
        "locale": "text",
    },
    "organisationContacts": {
        "organisationContactId": "text",
        "organisationContactType": "text",
        "organisationContactText": "text",
    },
    "organisationCode": "text",
    "organisationHomepage": "text",
    "domain": "text",
    "closedDate": "text",
    "organisationNumber": "text",
    "oldDivaDb": "text",
    "oldDivaId": "text",
    "oldParentId": "text",
    "organisationAlternativeNames": {
        "organisationName": {
            "organisationNameId": "text",
            "locale": "text",
            "organisationName": "text",
        }
    },
    "organisationAddress": {
        "addressId": "text",
        "postbox": "text",
        "street": "text",
        "postnumber": "text",
        "city": "text",
        "country": fedora_country_spec,
    },
    "organisationPredecessorDescriptions": {
        "diva2.commons.aura.list.organisation.OrganisationPredecessorDescription": {
            "organisationPredecessorDescriptionId": "text",
            "predecessorId": "text",
            "description": "text",
        }
    },
    "controlled": "text",
    "notEligible": "text",
    "showInPortal": "text",
    "showInDefence": "text",
    "topLevel": "text",
    "organisationNameUncontrolled": "text",
}

# Add circular references
fedora_organisation_spec["organisationParents"] = {
    "organisation": fedora_organisation_spec,
}
fedora_organisation_spec["organisationPredecessors"] = {
    "organisation": fedora_organisation_spec,
}


fedora_person_spec: XMLSpec = {
    "firstName": "text",
    "lastName": "text",
    "localId": "text",
    "organisations": {
        "organisation": fedora_organisation_spec,
    },
    "email": "text",
    "birthYear": "text",
    "deathYear": "text",
    "title": "text",
    "researchGroup": "text",
    "identifiers": {
        "entry": {
            "personIdentifierType": "text",
            "personIdentifier": {
                "value": "text",
                "type": "text",
            },
        }
    },
    "authorityPid": "text",
}


fedora_language_spec: XMLSpec = {
    "languageCode3": "text",
    "languageCode2": "text",
    "languageNames": {
        "languageName": {
            "languageNameId": "text",
            "locale": "text",
            "languageName": "text",
        }
    },
    "showsOnList": "text",
}

fedora_publication_title_spec: XMLSpec = {
    "title": "text",
    "subTitle": "text",
    "language": fedora_language_spec,
}

fedora_publication_type_spec: XMLSpec = {
    "publicationTypeId": "text",
    "publicationTypeCode": "text",
    "openUrlType": "text",
    "publicationTypeNames": {
        "publicationTypeName": {
            "publicationTypeNameId": "text",
            "locale": "text",
            "publicationTypeName": "text",
        }
    },
    "roles": "text",
    "comprehensiveSummary": "text",
    "domainAdminOnly": "text",
    "contentTypes": "ignore",
}

fedora_content_type_spec: XMLSpec = {
    "contentTypeId": "text",
    "contentTypeCode": "text",
    "contentTypeNames": {
        "contentTypeName": {
            "contentTypeNameId": "text",
            "locale": "text",
            "contentTypeName": "text",
        }
    },
    "sortOrder": "text",
}

fedora_title_spec: XMLSpec = {
    "titleId": "text",
    "mainTitle": "text",
    "subTitle": "text",
    "locale": "text",
}

fedora_series_spec: XMLSpec = {
    "seriesId": "text",
    "seriesTitle": fedora_title_spec,
    "seriesAlternativeTitles": {"seriesAlternativeTitle": fedora_title_spec},
    "issn": "text",
    "eissn": "text",
    "url": "text",
    "keyTitle": "text",
    "contentType": fedora_content_type_spec,
    "format": {
        "formatId": "text",
        "formatCode": "text",
        "formatNames": {
            "formatName": {
                "formatNameId": "text",
                "locale": "text",
                "formatName": "text",
            }
        },
    },
    "notes": "text",
    "subjects": "ignore",
    "publicationType": fedora_publication_type_spec,
    "organisation": fedora_organisation_spec,
    "domain": "text",
    "closedDate": "text",
    "controlled": "text",
}
fedora_series_spec["relationships"] = {
    "seriesRelation": {
        "relationId": "text",
        "relationType": {
            "relationTypeId": "text",
            "relationTypeCode": "text",
            "relationTypeNames": {
                "relationTypeName": {
                    "relationTypeNameId": "text",
                    "locale": "text",
                    "relationTypeName": "text",
                }
            },
        },
        "relative": fedora_series_spec,
    }
}


fedora_subject_spec: XMLSpec = {
    "subjectId": "text",
    "subjectType": {
        "subjectTypeId": "text",
        "subjectTypeCode": "text",
        "subjectTypeNames": {
            "subjectTypeName": {
                "subjectTypeNameId": "text",
                "locale": "text",
                "subjectTypeName": "text",
            }
        },
    },
    "subjectNames": {
        "subjectName": {
            "subjectNameId": "text",
            "locale": "text",
            "subjectName": "text",
        }
    },
    "subjectCode": "text",
    "domain": "text",
    "notEligible": "text",
    "oldDivaDb": "text",
    "oldDivaId": "text",
    "organisations": {"organisation": fedora_organisation_spec},
}
fedora_subject_spec["parents"] = {"subject": fedora_subject_spec}
fedora_subject_spec["predecessors"] = {"subject": fedora_subject_spec}

fedora_funder_spec: XMLSpec = {
    "funderId": "text",
    "funderName": {"name": "text", "locale": "text"},
    "organisationNumber": "text",
    "funderAlternativeNames": {
        "diva2.commons.aura.list.funder.FunderName": {
            "funderNameId": "text",
            "locale": "text",
            "funderName": "text",
        }
    },
    "doi": "text",
}

fedora_abstract_spec: XMLSpec = {
    "language": fedora_language_spec,
    "text": "text",
}

fedora_entry_spec: XMLSpec = {
    "language": fedora_language_spec,
    "list": {
        "string": "text",
    },
}

fedora_student_degree_spec: XMLSpec = {
    "thesisLevel": {
        "thesisLevelId": "text",
        "thesisLevelCode": "text",
        "thesisLevelOldCode": "text",
        "thesisLevelNames": {
            "thesisLevelName": {
                "thesisLevelNameId": "text",
                "locale": "text",
                "thesisLevelName": "text",
            }
        },
        "degrees": "ignore",
        "domain": "text",
    },
    "universityPoints": {
        "points": "text",
        "name__sv": "text",
        "name__en": "text",
        "name__no": "text",
        "hp": "text",
    },
    "undergraduateSubject": fedora_subject_spec,
}

fedora_journal_spec: XMLSpec = {
    "journalId": "text",
    "nordicListId": "text",
    "journalType": {
        "journalTypeId": "text",
        "journalTypeCode": "text",
        "journalTypeNames": {
            "journalTypeName": {
                "journalTypeNameId": "text",
                "locale": "text",
                "journalTypeName": "text",
            }
        },
    },
    "journalTitle": fedora_title_spec,
    "printedIssn": "text",
    "electronicIssn": "text",
    "url": "text",
    "fridaLevel": fedora_frida_level_spec,
    "controlled": "text",
    "openAccess": "text",
    "subjects": "ignore",
    "relationships": "ignore",
}

fedora_attachment_spec: XMLSpec = {
    "mimeType": {
        "mimeTypeId": "text",
        "mimeTypeName": "text",
        "fileSuffix": "text",
        "datasetOnly": "text",
    },
    "fileLabel": {
        "fileLabelId": "text",
        "fileLabelCode": "text",
        "fileLabelNames": {
            "fileLabelName": {
                "fileLabelNameId": "text",
                "locale": "text",
                "fileLabelName": "text",
            }
        },
    },
    "fileName": "text",
    "fileSize": "text",
    "selectedFileName": "text",
    "path": "text",
    "checksums": {
        "checksum": {
            "type": "text",
            "digest": "text",
        }
    },
    "order": "text",
    "uploadDate": "text",
    "asyncUpload": "text",
    "availableUntil": "text",
    "availableFrom": "text",
    "tempAvailableFrom": "text",
    "deleteDate": "text",
    "onHold": "text",
    "deleted": "text",
    "prePrint": "text",
    "postPrint": "text",
    "print": "text",
    "archiveOnly": "text",
    "printOnDemand": "text",
    "toBePublished": "text",
    "toBeArchived": "text",
    "digitized": "text",
    "hasCoverPage": "text",
    "coverPageConditions": "text",
    "description": "text",
    "secrecyInfo": {
        "secrecy": "text",
    },
    "registrationNumber": "text",
}


fedora_publication_xml_spec: XMLSpec = {
    "contentType": fedora_content_type_spec,
    "publicationType": fedora_publication_type_spec,
    "pid": "text",
    "administrativeInfo": {
        "domain": "text",
        "creatorInfo": fedora_user_information_spec,
        "updaters": {"userInformation": fedora_user_information_spec},
        "createdDate": "text",
        "updatedDate": "text",
        "deletedDate": "text",
        "deleterInfo": fedora_user_information_spec,
        "fileUploadMessage": "text",
        "importSource": "text",
    },
    "publicationDate": "text",
    "authors": {"person": fedora_person_spec},
    "noOfContributors": "text",
    "originalPublicationTitle": fedora_publication_title_spec,
    "alternativePublicationTitles": {"title": fedora_publication_title_spec},
    "seriesInfos": {
        "seriesInfo": {"series": fedora_series_spec, "numberInSeries": "text"}
    },
    "uncontrolledSeriesInfo": {
        "series": {
            "seriesAlternativeTitles": {},  # Always empty for uncontrolled series
            "issn": "text",
            "eissn": "text",
            "subjects": {},  # Always empty for uncontrolled series
            "relationships": {},  # Always empty for uncontrolled series
            "seriesNameUncontrolled": "text",
            "controlled": "text",
        },
        "numberInSeries": "text",
    },
    "dateIssued": "text",
    "conference": "text",
    "pages": "text",
    "edition": "text",
    "volume": "text",
    "issueNumber": "text",
    "startPage": "text",
    "endPage": "text",
    "distributor": "ignore",
    "distributorAsDist": "ignore",
    "publisher": {
        "city": "text",
        "publisherName": "text",
        "publishingHouse": {
            "externalId": "text",
            "publishingHouseId": "text",
            "name": "text",
            "nordicListId": "text",
            "fridaLevel": fedora_frida_level_spec,
        },
    },
    "urls": {
        "url": {
            "url": "text",
            "label": "text",
            "openAccess": "text",
        }
    },
    "isrn": "text",
    "localId": "text",
    "archiveNumber": "text",
    "pmid": "text",
    "isi": "text",
    "scopusId": "text",
    "nbn": "text",
    "isbnNumbers": {
        "isbn": {
            "number": "text",
            "type": "text",
        },
    },
    "identifiers": {
        "entry": {
            "publicationIdentifierType": "text",
            "publicationIdentifier": {
                "value": "text",
                "type": "text",
                "openAccess": "text",
                "alternativeValues": {
                    "value": {
                        "content": "text",
                    }
                },
            },
        }
    },
    "categories": {"subject": "ignore"},  # Old SVEP categories are ignored
    "nationalCategories": {"subject": fedora_subject_spec},
    "researchSubjects": {"subject": fedora_subject_spec},
    "keyWords": {"entry": fedora_entry_spec},
    "projects": {"project": {"projectName": "text"}},
    "projectRelations": {
        "projectRelation": {
            "relation": {
                "relationId": "text",
                "code": "text",
                "relationName": "text",
                "alternativeNames": {
                    "relationAlternativeName": {
                        "relationNameId": "text",
                        "locale": "text",
                        "relationName": "text",
                        "helpMessage": "text",
                    }
                },
            },
            "pid": "text",
        }
    },
    "abstracts": {"abstract": fedora_abstract_spec},
    "defence": {
        "date": "text",
        "language": fedora_language_spec,
        "room": {
            "name": "text",
            "street": "text",
            "city": "text",
        },
        "grantingInstitution": fedora_organisation_spec,
        "externalGrantingInstitution": "text",
    },
    "degree": {
        "degreeId": "text",
        "degreeNames": {
            "degreeName": {
                "degreeNameId": "text",
                "locale": "text",
                "degreeName": "text",
            }
        },
        "organisations": {"organisation": fedora_organisation_spec},
        "oldDivaDb": "text",
        "oldDivaId": "text",
        "domain": "text",
        "active": "text",
    },
    "note": "text",
    "internalNote": "text",
    "organisations": {"organisation": fedora_organisation_spec},
    "articleId": "text",
    "artisticWork": "text",
    "oai": "text",
    "patentDate": "text",
    "patentNumber": "text",
    "patentOrganisation": "text",
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
                    "roleId": "text",
                    "marcCode": "text",
                    "roleNames": {
                        "roleName": {
                            "roleNameId": "text",
                            "locale": "text",
                            "roleName": "text",
                        }
                    },
                }
            },
        }
    },
    "editors": {"person": fedora_person_spec},
    "bookTitle": {"title": "text", "subTitle": "text"},
    "bookEditor": "text",
    "proceedingsTitle": {"title": "text", "subTitle": "text"},
    "proceedingsEditor": "text",
    "funderInfos": {
        "funderInfo": {
            "funder": fedora_funder_spec,
            "projectNumber": "text",
        }
    },
    "geoData": {
        "description": "text",
        "westBoundLongitude": "text",
        "eastBoundLongitude": "text",
        "northBoundLatitude": "text",
        "southBoundLatitude": "text",
        "startDate": "text",
        "endDate": "text",
    },
    "externalCooperation": {
        "external": "text",
        "partners": {
            "partner": {
                "name": "text",
            }
        },
    },
    "academicTerm": {
        "year": "text",
        "term": "text",
    },
    "subtype": {
        "publicationSubtypeId": "text",
        "publicationSubtypeCode": "text",
        "publicationSubtypeNames": {
            "publicationSubtypeName": {
                "publicationSubtypeNameId": "text",
                "locale": "text",
                "publicationSubtypeName": "text",
            }
        },
    },
    "reviewed": "text",
    "reviewedBefore": "text",
    "failed": "text",
    "hidden": "text",
    "migrated": "text",
    "version": "text",
    "agreementAccepted": "text",
    "importDuplicate": "text",
    "registratedDuplicate": "text",
    "publicationStatus": {
        "publicationStatusId": "text",
        "publicationStatusNames": {
            "publicationStatusName": {
                "publicationStatusNameId": "text",
                "locale": "text",
                "publicationStatusName": "text",
            }
        },
        "code": "text",
    },
    "formatElectronic": "text",
    "formatPrint": "text",
    "responsibleOrganisation": {"organisation": fedora_organisation_spec},
    "canOrderOnline": "text",
    "publicationOrder": {
        "orderProfileId": "text",
        "orderURL": "text",
        "orderLink": "text",
        "validFrom": "text",
        "parameters": {
            "parameterEditor": {
                "paramKey": "text",
                "paramLabel": "text",
                "paramValue": "text",
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
        "size": "text",
        "duration": "text",
    },
    "publicationChannel": "text",
    "studentDegrees": {
        "studentDegree": fedora_student_degree_spec,
    },
    "uppsokSubject": "ignore",
    "journal": fedora_journal_spec,
    "uncontrolledJournal": {
        "printedIssn": "text",
        "electronicIssn": "text",
        "journalNameUncontrolled": "text",
        "controlled": "text",
        "openAccess": "text",
        "subjects": "ignore",
        "relationships": "ignore",
    },
    "sustainableDevelopments": {
        "sustainableDevelopment": {
            "developmentId": "text",
            "domain": "text",
            "name": {
                "name": "text",
                "locale": "text",
            },
            "alternativeNames": {
                "sustainableDevelopmentName": {
                    "developmentNameId": "text",
                    "name": {
                        "name": "text",
                        "locale": "text",
                    },
                }
            },
        },
    },
    "mediaType": {
        "autoId": "text",
        "code": "text",
        "names": {
            "mediaTypeName": {
                "autoId": "text",
                "locale": "text",
                "name": "text",
            }
        },
    },
    "attachments": {"no-comparator": "text", "attachment": fedora_attachment_spec},
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
            "relationId": "text",
            "code": "text",
            "relationName": "text",
            "alternativeNames": {
                "relationAlternativeName": {
                    "relationNameId": "text",
                    "locale": "text",
                    "relationName": "text",
                    "helpMessage": "text",
                }
            },
        },
        "relatedPid": "text",
        "relatedPublication": fedora_publication_xml_spec,
    }
}
