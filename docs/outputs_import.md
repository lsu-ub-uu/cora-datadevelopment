# Outputs import

This script imports outputs from XML files exported from Diva Classic database, transforms them to Cora format and imports them to the specified DiVA Cora system.

## Prerequisites

- Python 3 and PIP installed
- An XML file with exported outputs from DiVA Classic Database
- Binaries that are referenced by attachments are saved in the `binaries` subdirectory
- **Important**: Publishers, Funders, Journals, Subjects, Series and Organisations that are referenced by the outputs that are to be imported, have already been imported to the Cora systemc

## Installing the package

```bash
pip install .
```

## Running the script (dry run)

```bash
outputs-import --xml-dir path/to/outputs --system mig
```

## Running the script and create records in Cora

```bash
outputs-import --xml-dir path/to/outputs --system mig --apply
```

## Show script help, with all available parameters

```bash
outputs-import --help
```

## Detailed information about field mapping

Below is specified how each field in the Cora diva-output metadata model is mapped from the DiVA Classic publication model.

- recordInfo
  - validationType <- Mapping from `publicationType/publicationTypeCode` and `subtype/publicationSubtypeCode`
  - permissionUnit <- `administrativeInfo/domain`
  - oldId <- `pid`
  - ⚠️ visibility <- Logic based on `administrativeInfo/updaters/userInformation/userAction` and `administrativeInfo/creatorInfo/userAction` ⚠️ Needs updating when changes to visibility is done in Cora
- dataQuality <- `2026` if validation passes, otherwise `classic`
- genre type="contentType" <- Mapping from `contentType/contentTypeCode`,
- titleInfo <- `originalPublicationTitle`
  - title <- `title`
  - subtitle `subtitle`
  - language <- `language/languageCode3` (behöver val "undefined" i classic valideringstyp)
- subject <- `keyWords`
  - topic <- > `keyWords/entry/list/string`
  - language <- `keyWords/entry/language/languageCode3`
- genre type="outputType" (valideringstyp) <- Same as validationType (see above)
- language <- `originalPublicationTitle/language` (Classic does not have a language for the publication, we'll use the langue from the main title.)
- artisticWork type="outputType" <- `artisticWork` if the tag is missing, it will be missing in cora
- titleInfo type="alternative" <- `alternativePublicationTitles/title`
  - title <- `title`
  - subtitle `subtitle`
  - language <- `language/languageCode3`
- name type="personal" <- ` authors/person` , ` editors/person` , `otherContributors/contributor`
- ⚠️ person (link to migrated record) <- `authorityPid`

  - namePart type="family" <- `lastName`
  - namePart type="given" <- `firstName`
  - namePart type="date" <- `birthYear-deathYear` only birthYear: "1988" birth and death year: "1988-2050" only deathYear: "-1850"
  - role/roleTerm <- aut | edt | `roles/role/marcCode`
  - orcid <- `identifiers/entry/personIdentifier/value` where type is "orcid"
  - lokalt id <- `localId` ⚠️ Some members need local ids to not be publically visible. Solution needed.
  - affiliations <- `organisations/organisation`, ⚠️ `researchGroup` should probably be an affiliation with description "Research group". waiting for decision.
    - organisation (link to migrated record) <- `organisation/organisationId`
    - name type="corporate" <- `organisation/organisationNameUncontrolled`
    - 🆕 identifier type="ror" <- N/A
    - 🆕 country <- N/A
    - description <- N/A

- name type="personal" otherType="degreeSupervisor" <- `supervisors` ⚠️ Metadata will change to move to <name type="personal">
- same as name type="personal"
- title ?
- Name type="personal" otherType="thesisAdvisor" <- `examiners` ⚠️ Metadata will change to move to <name type="personal">
- name type="personal" otherType="opponent" <- `opponents` ⚠️ Metadata will change to move to <name type="personal">
- 🔨 name type="corporate" <- `responsibleOrganisations`
  - organisation (link to migrated record) <- `organisation/organisationId`
  - role/roleTerm <- "cre"
- note type="creatorCount" <- `noOfContributors`
- ⚠️ abstract <- `abstracts/abstract/text` HTML formatting is converted to plain text. ⚠️ Does not yet handle latex or image tags
  - language <- `language/languageCode3`
- originInfo
  - ⚠️ dateIssued/year <- `dateIssued` ⚠️ Newspaper articles may contain month and day. Needs to handle iso dates.
  - 🆕 copyrightDate <- N/A
  - 🆕 dateOther type="online" <- N/A
  - agent
    - publisher (link) <-`publishingHouse/publishingHouseId`
    - namePart <- `publisherName`
  - place/placeTerm <- `publisher/city`
  - edition <- `edition`
- classification authority="ssif" <- `nationalCategories/subject/subjectCode`
- subject authority="diva"<- `researchSubjects`
  - topic (link to migrated record) <- `subject/subjectId`
- subject authority="sdg" <- `sustainableDevelopments` ⚠️ Some ids cannot be mapped to sdg codes.

  - topic <- mappning av `sustainableDevelopment/developmentId`

  ======= Reviewed to this point =========

- identifier type="isbn" <- `isbnNumbers/isbn/number` if not chapter or conference paper
  - displayLabel <- mappning från `isbNumbers/isbn/type`
- identifier type="doi" <- `identifiers/entry/publicationIdentifier/value` where (`publicationIdentifierType == "doi"`) if not chapter or conference paper
- 🆕 identifier type="ismn" <- N/A
- identifier type="archiveNumber"> <- `archiveNumber`
- 🆕 identifier type="openAlex"
- identifier type="se-libr" <- `identifiers/entry/publicationIdentifier/value` where (`publicationIdentifierType == "libris"`)
- identifier type="localId" <- `localId`
- identifier type type="pmid" <- `pmid`
- identifier type type="wos" <- `isi`
- identifier type type="scopus" <- `scopusId`
- identifier type="isrn" <- `isrn`
- location <- `urls/url`
  - url <-`url/url`
  - displayLabel <- `url/label`
- ⚠️ location displayLabel="orderLink" Need to check what to set as displayLabel
  - url <- `publicationOrder/orderURL`
  - displayLabel <- Leave blank or determine based on orderProfileId ❓
- note type="external" <- `note`
- relatedItem type="series" otherType="link" <- `seriesInfos/seresInfo`
  - series (link to migrated record) <- `series/seriesId`
  - partNumber <- `numberInSeries`
- relatedItem type="series" otherType="text" <- `uncontrolledSeriesInfo`
  - titleInfo
    - title <- `series/seriesNameUncontrolled`
    - subTitle <- N/A
  - identifier type="issn" displayLabel="pissn" <- `series/issn`
  - identifier type="issn" displayLabel="eissn" <- `series/eissn`
  - partNumber <- `numberInSeries`
- 🆕 relatedItem type="researchData" <- N/A
- relatedItem type="project" otherType="link" <- `projectRelations/projectRelation`
  - project (link to migrated record) <- `pid`
- relatedItem type="project" otherType="text" <- `projects`
  - titleInfo/title <- `project/projectName`
  - titleInfo/subTitle <- N/A
- 🆕 relatedItem type="initiative"
- 🆕 accessCondition authority="kb.se"
- 🆕 localGenericMarkup
- adminInfo
  - failed <- `failed`
  - reviewed <- `reviewed`
  - note type="internal" <- `internalNote`
- genre type="subcategory" <- `subType` subTypeId 66=policyDocument 3=exhibitionCatalog Not done
- note type="publicationStatus" <- `publicationStatus`
- typeOfResource <- `mediaType`
- type <- `mediaInformation/types`
- material <- `mediaInformation/materials`
- technique <- `mediaInformation/techniques`
- size <- `mediaInformation/size`
- duration <- `mediaInformation/duration`
- ⚠️ physicalDescription <- `pages` `mediaInformation/physicalDescriptions` Not done. Needs output-test.
- 🆕 note type="context" <- N/A ❓
- dateOther type="patent" <- `patentDate` Not done. Needs output-test.
- identifier type="patentNumber" <- `patentNumber`
- patentHolder type="corporate" ❓
  - namePart <- `patentOrganisation`
  - 🆕 identifier type="ror" <- N/A ❓
  - 🆕 description <- N/A ❓
- patentCountry <- `patentCountry/countryCode`

- academicSemester <- `academicTerm`
  - year <- `year`
  - academicSemester <- `term` (to lower case)
- studentDegree <- `studentDegrees`
  - degreeLevel <- `studentDegree/thesisLevel/thesisLevelCode`
  - universityPoints <- `studentDegree/universityPoints/hp`
  - course (link to migrated record) <- `studentDegree/undergraduateSubject/subjectId`
  - programme (link to migrated record) <- `studentDegree/educationalProgramme/subjectId`
- externalCollaboration <- `externalCooperation`
  - namePart <- `partners/partner/name` If `external` is true and no partner name exists, a default text "Externt samarbete" is set.
- degreeGrantingInstitution type="corporate" otherType="link" <- `defence/grantingInstitution`
  - organisation (link to migrated record) <- `organisationId`
- degreeGrantingInstitution type="corporate" otherType="text" <- `defence/externalGrantingInstitution`
  - namePart <- `externalGrantingInstitution`
  - 🆕 identifier type="ror" <- N/A
- defence <- `defence` For degree project (diva-degreeProject) the tag should be presentation instead of defence.
- presentation <- `defence` See above
  - `language` <- `languageTerm/language`
  - `dateOther` <- `date`
  - `location` <- `room> <name`
  - `address` <- `room/street`
  - `place/placeTerm` <- `room/city`
  - `degreeGrantingInstitution` <- `grantingInstitution`
  - `organisation` <- `organisationId`
- relatedItem type="journal" otherType="link" <- `journal`
  - journal (link to migrated record) <- `journalId`
    - part Nedanstående taggar finns direkt under `publication`.
      - detail type="volume" <- `volume`
        - number
      - detail type="issue" <- `issueNumber`
        - number
      - detail type="artNo" `articleId`
      - extent
        - start <- `startPage`
        - end <- `endPage`
- relatedItem type="journal" otherType="text" <- `uncontrolledJournal`
  - titleInfo
    - title <- `journalNameUncontrolled`
    - subTitle <- N/A
  - identifier type="issn" displayLabel="pissn" <- `printedIssn`
  - identifier type="issn" displayLabel="eissn" <- `electronicIssn`
  - part Nedanstående taggar finns direkt under `publication`. Not done
    - detail type="volume" <- `volume`
      - number
    - detail type="issue" <- `issueNumber`
      - number
    - detail type="artNo" `articleId`
    - extent
      - start <- `startPage`
      - end <- `endPage`
- 🆕 relatedItem type="book" otherType="link"
  - book
- relatedItem type="book" otherType="text"

  - titleInfo `bookTitle`
    - title <- `title`
    - subtitle <- `subtitle`
    - language ❓
  - note type="statementOfResponsibility" <- `bookEditor`
  - identifier type="isbn" <- `isbnNumbers/isbn/number` For chapters, isbn is on the book and not directly on the output
  - identifier type="doi" <- `identifiers/entry/publicationIdentifier/value` where (`publicationIdentifierType == "doi"`) For chapters doi is on the book and not the output
    ❓ should we skip libris?
  - part/extent
    - start <- `startPage`
    - end <- `endPage`
  - relatedItem type="series" otherType="link"
  - relatedItem type="series" otherType="text"

- 🆕 relatedItem type="conferencePublication" otherType="link"
  - proceeding (link to migrated record)
- relatedItem type="conferencePublication" otherType="text"
  - titleInfo <- `proceedingsTitle`
    - title <- `title`
    - subtitle <- `subtitle`
    - language
  - note type="statementOfResponsibility" <- `proceedingsEditor`
  - identifier type="isbn" <- `isbnNumbers/isbn/number` For conference paper, isbn should be on the conferencePublication and not directly on the output
  - identifier type="doi" `identifiers/entry/publicationIdentifier/value` where (`publicationIdentifierType == "doi"`) For conference paper doi is on the conferencePublication and not the output
  - part/extent
    - start <- `startPage`
    - end <- `endPage`
  - relatedItem type="series" otherType="link"
  - relatedItem type="series" otherType="text"
- relatedItem type="conference" <- `conference`
- relatedItem type="funder"
  - funder (link to migrated record) <- `funderInfos/funder/funderId`
  - identifier type="project" <- `funderInfos/funderId/projectNumber`
- 🆕 related <- N/A
- 🆕 related type="retracted" <- N/A
- ⚠️ related type="constituent" (link to migrated recordade avhandligar)
  - output (link to migrated record) <- `partsOfPublication/publication/pid`
- relatedItem type="publicationChannel"
  - publicationChannel <- `publicationChannel`

### Needs more information

- `hidden` - Om true visas posten ej i sökgränssnittet. Och måste sökas fram med särskild flagga. kommer behöva hanteras vid migrering. Kanske blir visibility: unpublished?

### Taggar ej i Cora

- `reviewedBefore`
- `distributor`
- `distributorAsDist`
- `formatElectronic`
- `formatPrint`
- `canOrderOnline`
- `migrated`
- `version`
- `registratedDuplicate`
- `importDuplicate`
- `categories`
- ⚠️ `imprint` (Only for Uppsala University)

## Binary

- binary <- `attachments/attatchment`

  - recordInfo
    - visibility <-- från `deleted`, `onHold`, `availableFrom`, `availableUntil`
  - originalFileName <- `path` with only the content after the /
  - expectedFileSize <- `fileSize`
  - expectedChecksum <- `checksums/checksum/digest`
  - visibility
  - type="generic"

- attachment
  - `agreementAccepted` - Check this
