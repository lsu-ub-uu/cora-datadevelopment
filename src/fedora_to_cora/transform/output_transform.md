## Status för convertering

## Binary

- binary
  - recordInfo
    - visibility <-- från `deleted`, `onHold`, `availableFrom`, `availableUntil`
  - originalFileName <- `path` samt skippa allt efter /
  - expectedFileSize <- `fileSize`
  - expectedChecksum <- `attachments/attachment/checksums/checksum/digest`
  - visibility
  - type="generic"

## Output

### Behövs för Sammlingsverk

- ✅ recordInfo
  - ✅ validationType <- `publicationType/publicationTypeId`
  - ✅ permissionUnit <- `domain`
  - ✅ oldId <- `pid`
  - ✅ visibility <- `administrativeInfo/updaters/userInformation/userAction`
  - ✅ genre type="contentType" <- `contentType/contentTypeCode`
- ✅ titleInfo type="main" <- `originalPublicationTitle`
- ✅ subject <- `keyWords`
- ✅ genre type="outputType" (valideringstyp) <- `publicationType` via `get_validation_type_by_publication_typ`
- ✅ language <- `originalPublicationTitle/language`
- ✅ artisticWork type="outputType" <- `artisticWork`
- ✅ titleInfo type="alternative" <- `alternativePublicationTitles`
- ✅ name type="personal" <-

  ```xml
  <authors/person>
  <editors/person>
  <examiners/person>
  <supervisors/person>
  <opponents/person>
  ```

- ❌ name type="corporate" <- skipped
- ✅ note type="creatorCount"
- ✅ abstract <- `abstracts/abstract`

- originInfo
  - ✅ dateIssued <- `publicationDate`
  - ❌copyrightDate <- skipped
  - ❌ dateOther type="online" <- skipped
  - ✅ agent <- `publisher/publisherName`
  - ✅ place <- `publisher/city`
  - ✅ edition <- `edition`
- ✅ extent <- `pages`
- ✅ classification authority="ssif" <- `nationalCategories/subject/subjectCode`
- ✅ subject authority="diva" <- `researchSubjects`
- ✅ subject authority="sdg" <- `sustainableDevelopments` (värden som inte är giltiga för valideringen behöver uppdateras)
- ✅ identifier type="isbn" <- `isbn`
- ✅ identifier type="doi" <- `identifiers/entry/publicationIdentifierType>doi`
- 🆕 identifier type="ismn"
- ✅ identifier type="archiveNumber"> <- `archiveNumber`
- 🆕 identifier type="openAlex"
- ✅ identifier type="se-libr" <- `identifiers/entry/publicationIdentifierType>libris`
- ✅ identifier type="localId" <- `localId`
- ✅ identifier type type="pmid" <- `pmid`
- ✅ identifier type type="wos" <- `isi`
- ✅ identifier type type="scopus" <- `scopusId`
- ✅ location <- `urls/url` (openAccess behöver hanteras)
- location displayLabel="orderLink" (Kolla upp orderProfileId i höst, är generiska texter i Classic för displayLabel, url från orderURL)
- ✅note type="external" <- `note`
- ✅ relatedItem type="series" <- `seriesInfo` och `uncontrolledSeriesInfo`
  - ✅ series <- `seriesInfo`
  - ✅ titleInfo/mainTitle <- `uncontrolledSeriesInfo/series/seriesNameUncontrolled`
  - ✅ identifier type="issn" displayLabel="pissn" <- `uncontrolledSeriesInfo/series/issn`
  - ✅ identifier type="issn" displayLabel="eissn" <- `uncontrolledSeriesInfo/series/eissn`
  - ✅ partNumber <- `uncontrolledSeriesInfo>numberInSeries` (?)
  - ❌ No mapping: `uncontrolledSeriesInfos/seriesAlternativeTitles>, subjects, <relationships`
- 🆕 relatedItem type="researchData"
- ✅ relatedItem type="project" <- `projects`
- 🆕 relatedItem type="initiative"
- 🆕 accessCondition authority="kb.se"
- 🆕 localGenericMarkup
- ✅ adminInfo
  - ✅ failed <- `failed`
  - ✅ reviewed <- `reviewed`
  - ✅ note type="internal" <- `internalNote`

### Behövs för Samlingsverk Update

- attachment
  - `agreementAccepted` - kanske inte sparas?

### Behövs ej för Sammlingsverk

- genre type="subcategory" <- `subType` (behöver mappas om till värden i Cora)
- note type="publicationStatus" <- `publicationStatus` (behöver mappas om till värden i Cora)
- ✅ typeOfResource <- `mediaType`
- ✅ type <- `mediaInformation/physicalDescriptions`
- ✅ material <- `mediaInformation/materials`
- ✅ technique <- `mediaInformation/techniques`
- ✅ size <- `mediaInformation/size`
- ✅ duration <- `mediaInformation/duration`
- ✅ physicalDescription <- `mediaInformation/physicalDescriptions`
- ✅ dateOther type="patent" <- `patentDate`
- imprint (Gäller bara UU)
- ✅ identifier type="patentNumber" <- `patentNumber`
- ✅ identifier type="isrn" <- `isrn`
- ✅ academicSemester <- `academicTerm`
- ✅ studentDegree <- `studentDegrees`
  - ✅ degreeLevel <- `studentDegree/thesisLevel/thesisLevelCode`
  - ✅ universityPoints <- `studentDegree/universityPoints/hp`
  - ✅ course <- link to diva-course by oldId: `studentDegree/undergraduateSubject/subjectId`
  - ✅ programme <- link to diva-programme by oldId: `studentDegree/educationalProgramme/subjectId`
- ✅ externalCollaboration <- `externalCooperation`
- ✅ degreeGrantingInstitution type="corporate" <- `defence/grantingInstitution`
  - ✅ organisation
  - ✅ namePart
  - ✅ role
  - 🆕 identifier type="ror" (ROR finns inte i Classic)
- presentation <- `defence` (Kolla om både presentation och defence behöver hanteras)
- ✅ defence <- `defence`

  - ✅ `language` <- `languageTerm/language`
  - ✅ `dateOther` <- `date`
  - ✅ `location` <- `room> <name`
  - ✅ `address` <- `room/street`
  - ✅ `place/placeTerm` <- `room/city`
  - ✅ `degreeGrantingInstitution` <- `grantingInstitution`
  - `organisation` <- `organisationId`

- relatedItem type="journal" <- `journal`
  - ✅ journal
  - ✅ titleInfo
    - ✅ title
    - ✅ subTitle
  - ✅ identifier type="issn" displayLabel="pissn"
  - ✅ identifier type="issn" displayLabel="eissn"
  - part
    - detail type="volume" <- `volume`
      - number
    - detail type="issue" <- `issueNumber`
      - number
    - detail type="artNo" `articleId`
    - extent
      - start <- `startPage`
      - end <- `endPage`
- relatedItem type="book" <- `bookTitle` och `bookEdition` <- `statmentOfResponsibility` som barnelement i Cora
- relatedItem type="conferencePublication" <- `proceedingsTitle` och `proceedingsEditor` <- `statmentOfResponsibility` som barnelement i Cora
- relatedItem type="conference" <- `conference`
- relatedItem type="funder" <- `funderInfos/funderId/projectNumber`
- 🆕 related
- 🆕 related type="retracted"
- related type="constituent" (länkade avhandligar)
- note type="statementOfResponsibility"/

## Behöver mer information för att migrera

- `hidden` - Om true visas posten ej i sökgränssnittet. Och måste sökas fram med särskild flagga. kommer behöva hanteras vid migrering. Kanske blir visibility: unpublished?
- `publicationChannel` - Används för konstnärlig output. Metadata ej klar i Cora.

## Taggar ej i Cora

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
