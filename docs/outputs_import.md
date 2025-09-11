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
  - validationType <- [Mapping](./get_validation_type_by_publication_type_id.py) from `publicationType/publicationTypeId`
  - permissionUnit <- `administrativeInfo/domain`
  - oldId <- `pid`
  - visibility <- [Logic](./get_visibility.py) based on `administrativeInfo/updaters/userInformation/userAction` and `administrativeInfo/creatorInfo/userAction`
- genre type="contentType" <- Mapping from `contentType/contentTypeCode`
- titleInfo <- `originalPublicationTitle`
- subject <- `keyWords` (language from `language/languageCode3`)
- genre type="outputType" (valideringstyp) <- [Mapping](./get_validation_type_by_publication_type_id.py) from `publicationType/publicationTypeId` (same as validation type)
- language <- `originalPublicationTitle/language`
- artisticWork type="outputType" <- `artisticWork`
- titleInfo type="alternative" <- `alternativePublicationTitles`
- name type="personal" <- merge ` authors/person` , ` editors/person` , ` examiners/person` , ` supervisors/person` , ` opponents/personal` ⚠️ Linked persons are not handled
- 🆕 name type="corporate" <- skipped
- note type="creatorCount" <- `noOfContributors`
- abstract <- `abstracts/abstract`
- originInfo
  - dateIssued <- `publicationDate`
  - 🆕 copyrightDate <- skipped
  - 🆕 dateOther type="online" <- skipped
  - agent <- `publisher/publisherName` and `publishingHouse/publishingHouseId`
  - place <- `publisher/city`
  - edition <- `edition`
- extent <- `pages`
- classification authority="ssif" <- `nationalCategories/subject/subjectCode`
- subject authority="diva" <- `researchSubjects`
- subject authority="sdg" <- `sustainableDevelopments`
- identifier type="isbn" <- `isbn`
- identifier type="doi" <- `identifiers/entry/publicationIdentifierType>doi`
- 🆕 identifier type="ismn"
- identifier type="archiveNumber"> <- `archiveNumber`
- 🆕 identifier type="openAlex"
- identifier type="se-libr" <- `identifiers/entry/publicationIdentifierType>libris`
- identifier type="localId" <- `localId`
- identifier type type="pmid" <- `pmid`
- identifier type type="wos" <- `isi`
- identifier type type="scopus" <- `scopusId`
- location <- `urls/url` (⚠️ openAccess behöver hanteras. Ska det in på accessCondition authority="kb.se"?)
- ⚠️ location displayLabel="orderLink" (Kolla upp orderProfileId i höst, är generiska texter i Classic för displayLabel, url från orderURL)
- note type="external" <- `note`
- relatedItem type="series" <- `seriesInfo` och `uncontrolledSeriesInfo`
  - series <- `seriesInfo`
  - titleInfo/mainTitle <- `uncontrolledSeriesInfo/series/seriesNameUncontrolled`
  - identifier type="issn" displayLabel="pissn" <- `uncontrolledSeriesInfo/series/issn`
  - identifier type="issn" displayLabel="eissn" <- `uncontrolledSeriesInfo/series/eissn`
  - partNumber <- `uncontrolledSeriesInfo/numberInSeries` (?)
  - ❌ No mapping: `uncontrolledSeriesInfos/seriesAlternativeTitles, subjects, relationships` (⚠️ behöver de tas hand om?)
- 🆕 relatedItem type="researchData"
- relatedItem type="project" <- `projects`
- 🆕 relatedItem type="initiative"
- 🆕 accessCondition authority="kb.se" (⚠️ Ligger på post nivå, inte per url)
- 🆕 localGenericMarkup
- adminInfo
  - failed <- `failed`
  - reviewed <- `reviewed`
  - note type="internal" <- `internalNote`

### Fields not yet mapped:

- genre type="subcategory" <- `subType` (⚠️ behöver mappas om till värden i Cora)
- note type="publicationStatus" <- `publicationStatus` (⚠️ behöver mappas om till värden i Cora)
- typeOfResource <- `mediaType`
- type <- `mediaInformation/physicalDescriptions`
- material <- `mediaInformation/materials`
- technique <- `mediaInformation/techniques`
- size <- `mediaInformation/size`
- duration <- `mediaInformation/duration`
- physicalDescription <- `mediaInformation/physicalDescriptions`
- dateOther type="patent" <- `patentDate`
- ⚠️ imprint (Only for Uppsala University)
- identifier type="patentNumber" <- `patentNumber`
- identifier type="isrn" <- `isrn`
- academicSemester <- `academicTerm`
- studentDegree <- `studentDegrees`
  - degreeLevel <- `studentDegree/thesisLevel/thesisLevelCode`
  - universityPoints <- `studentDegree/universityPoints/hp`
  - course <- link to diva-course by oldId: `studentDegree/undergraduateSubject/subjectId`
  - programme <- link to diva-programme by oldId: `studentDegree/educationalProgramme/subjectId`
- externalCollaboration <- `externalCooperation`
- degreeGrantingInstitution type="corporate" <- `defence/grantingInstitution`
  - organisation
  - namePart
  - role
  - 🆕 identifier type="ror" (ROR finns inte i Classic)
- ⚠️ presentation <- `defence` (Kolla om både presentation och defence behöver hanteras)
- defence <- `defence`

  - `language` <- `languageTerm/language`
  - `dateOther` <- `date`
  - `location` <- `room> <name`
  - `address` <- `room/street`
  - `place/placeTerm` <- `room/city`
  - `degreeGrantingInstitution` <- `grantingInstitution`
  - `organisation` <- `organisationId`

- relatedItem type="journal" <- `journal`
  - journal
  - titleInfo
    - title
    - subTitle
  - identifier type="issn" displayLabel="pissn"
  - identifier type="issn" displayLabel="eissn"
  - ⚠️ part
    - ⚠️detail type="volume" <- `volume`
      - ⚠️ number
    - ⚠️ detail type="issue" <- `issueNumber`
      - ⚠️ number
    - ⚠️ detail type="artNo" `articleId`
    - ⚠️ extent
      - ⚠️ start <- `startPage`
      - ⚠️ end <- `endPage`
- ⚠️ relatedItem type="book" <- `bookTitle` och `bookEdition` <- `statmentOfResponsibility` som barnelement i Cora
- ⚠️ relatedItem type="conferencePublication" <- `proceedingsTitle` och `proceedingsEditor` <- `statmentOfResponsibility` som barnelement i Cora
- ⚠️ relatedItem type="conference" <- `conference`
- ⚠️ relatedItem type="funder" <- `funderInfos/funderId/projectNumber`
- 🆕 related
- 🆕 related type="retracted"
- ⚠️ related type="constituent" (länkade avhandligar)
- ⚠️ note type="statementOfResponsibility"

### Behöver mer information för att migrera

- `hidden` - Om true visas posten ej i sökgränssnittet. Och måste sökas fram med särskild flagga. kommer behöva hanteras vid migrering. Kanske blir visibility: unpublished?
- `publicationChannel` - Används för konstnärlig output. Metadata ej klar i Cora.

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

## Binary

- binary <- `attachments/attatchment`
  - recordInfo
    - visibility <-- från `deleted`, `onHold`, `availableFrom`, `availableUntil`
  - originalFileName <- `path` with only the content after the /
  - expectedFileSize <- `fileSize`
  - expectedChecksum <- `checksums/checksum/digest`
  - visibility
  - type="generic"

### Behövs för Samlingsverk Update

- attachment
  - `agreementAccepted` - Check this
