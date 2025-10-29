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
  - ⚠️ validationType <- [Mapping](./get_validation_type_by_publication_type_id.py) from `publicationType/publicationTypeId` ⚠️ Behöver även ta hänsyn till subType
  - ✅ permissionUnit <- `administrativeInfo/domain`
  - ✅ oldId <- `pid`
  - ⚠️ visibility <- [Logic](./get_visibility.py) based on `administrativeInfo/updaters/userInformation/userAction` and `administrativeInfo/creatorInfo/userAction` ⚠️ Behöver uppdatera när Trash etc är färdigt
- ✅ genre type="contentType" <- Mapping from `contentType/contentTypeCode`
- ⚠️ titleInfo <- `originalPublicationTitle`
  - title <- `title` ⚠️ Strippar inte rich text
  - subtitle `subtitle`
  - language <- `language/languageCode3`
- subject <- `keyWords`
  - ⚠️ topic <- > `keyWords/entry/list/string` (byter ut mellanslag mot kommatecken) Hanterar inte multiple strings. ❓ Ev. ändra Cora modell?
  - language <- `keyWords/entry/language/languageCode3`
- ⚠️ genre type="outputType" (valideringstyp) <- [Mapping](./get_validation_type_by_publication_type_id.py) from `publicationType/publicationTypeId` (same as validation type) Behöver hantera subType
- ✅ language <- `originalPublicationTitle/language` (Classic har inget språk för publikationen. Vi använder oss av huvudtitelns språk.)
- ✅ artisticWork type="outputType" <- `artisticWork`
- ⚠️ titleInfo type="alternative" <- `alternativePublicationTitles/title`
  - title <- `title` ⚠️Strippar inte Rich text
  - subtitle `subtitle`
  - language <- `language/languageCode3`
- ⚠️ name type="personal" <- ` authors/person` , ` editors/person` , `otherContributors/contributor`
  - namePart type="family" <- `lastName`
  - namePart type="given" <- `firstName`
  - role/roleTerm <- aut | edt | `roles/role/marcCode`
  - ✅ affiliations <- `organisations/organisation` ,
    - organisation (länk) <- `organisation/organisationId`
    - name type="corporate" <- `organisation/organisationNameUnconrolled`
      ⚠️ orcid ❓ ska vi ignorera viaf och libris?
      ✅ lokalt id
- 🆕 name type="corporate" <- N/A
- ✅ note type="creatorCount" <- `noOfContributors`
- ⚠️ abstract <- `abstracts/abstract/text` Hanterar inte rich text och latex
  - language <- `language/languageCode3`
- ✅ originInfo
  - dateIssued/year <- `dateIssued` (Endast år anges i Classic)
  - 🆕 copyrightDate <- N/A
  - 🆕 dateOther type="online" <- N/A
  - ✅ agent
    - publisher (link) <-`publishingHouse/publishingHouseId`
    - namePart <- `publisherName`
  - place/placeTerm <- `publisher/city`
  - edition <- `edition`
- ✅ extent <- `pages`
- ✅ classification authority="ssif" <- `nationalCategories/subject/subjectCode`
- ✅ subject authority="diva"<- `researchSubjects`
  - topic (länk) <- `subject/subjectId`
- ✅ subject authority="sdg" <- `sustainableDevelopments`
  - topic <- mappning av `sustainableDevelopment/developmentId`
- ✅ identifier type="isbn" <- `isbnNumbers/isbn/number`
  - displayLabel <- mappning från `isbNumbers/isbn/type`
- identifier type="doi" <- `identifiers/entry/publicationIdentifier/value` där (`publicationIdentifierType == "doi"`)
- 🆕 identifier type="ismn" <- N/A
- ✅ identifier type="archiveNumber"> <- `archiveNumber`
- 🆕 identifier type="openAlex"
- ✅ identifier type="se-libr" <- `identifiers/entry/publicationIdentifier/value` där (`publicationIdentifierType == "libris"`)
- ✅ identifier type="localId" <- `localId`
- ✅ identifier type type="pmid" <- `pmid`
- ✅ identifier type type="wos" <- `isi`
- ✅ identifier type type="scopus" <- `scopusId`
- ✅ location <- `urls/url`
  - url <-`url/url`
  - displayLabel <- `url/label`
- ⚠️ location displayLabel="orderLink" (Kolla upp orderProfileId i höst, är generiska texter i Classic för displayLabel, url från orderURL)
- ⚠️ note type="external" <- `note` Hanterar ej Rich text
- ⚠️ relatedItem type="series" otherType="link" <- `seriesInfos/seresInfo`
  - series (länk) <- `series/seriesId`
  - ⚠️ partNumber <- `numberInSeries` ej klar
- ✅ relatedItem type="series" otherType="text" <- `uncontrolledSeriesInfo`
  - titleInfo
    - mainTitle <- `series/seriesNameUncontrolled`
    - subTitle <- N/A
  - identifier type="issn" displayLabel="pissn" <- `series/issn`
  - identifier type="issn" displayLabel="eissn" <- `series/eissn`
  - partNumber <- `numberInSeries`
- 🆕 relatedItem type="researchData" <- N/A
- ✅ relatedItem type="project" otherType="link" <- `projectRelations/projectRelation`
  - project (länk) <- `pid`
- ✅ relatedItem type="project" otherType="text" <- `projects`
  - titleInfo/title <- `project/projectName`
  - titleInfo/subTitle <- N/A
- 🆕 relatedItem type="initiative"
- 🆕 accessCondition authority="kb.se" (⚠️ Ligger på post nivå, inte per url)
- 🆕 localGenericMarkup
- ⚠️ adminInfo
  - failed <- `failed`
  - reviewed <- `reviewed`
  - ⚠️ note type="internal" <- `internalNote` Stödjer ej rich text

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
