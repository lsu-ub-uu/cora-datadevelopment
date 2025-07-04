# Cora data development

This repository contains scripts for creating and migrating data.

## Dev installation

```sh
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Run tests

```sh
pytest
```

## Run tests with coverage report

```sh
pytest --cov=src
```

## Run tests in watch mode

```sh
ptw --now .
```

## Status för convertering

## Behövs för Sammlingsverk

- ✅ recordInfo
  - ✅ validationType <- `<publicationType><publicationTypeId>`
  - ✅ permissionUnit <- domain
  - ✅ oldId <- `<pid>`
  - ✅ visibility <- `<administrativeInfo><updaters><userInformation><userAction>`
  - ✅ genre type="contentType" <- `<contentType><contentTypeCode>`
- ✅ titleInfo type="main" <- `<originalPublicationTitle>`
- ✅ subject <- `<keyWords>`
- ✅ genre type="outputType" (valideringstyp) <- `<publicationType>` via `get_validation_type_by_publication_typ`
- ✅ language <- `<originalPuoriblicationTitle><language>`
- ✅ artisticWork type="outputType" <- `<artisticWork>`
- ✅ titleInfo type="alternative" <- `<alternativePublicationTitles>`
- ✅ name type="personal" <-

  ```xml
  <authors><person>
  <editors><person>
  <examiners><person>
  <supervisors><person>
  <opponents><person>
  ```

- ❌ name type="corporate" <- skipped
- ✅ note type="creatorCount"
- ✅ abstract <- `<abstracts><abstract>`

- originInfo
  - ✅ dateIssued <- `<publicationDate>`
  - ❌copyrightDate <- skipped
  - ❌ dateOther type="online" <- skipped
  - ✅ agent
  - ✅ place
  - ✅ edition
- ✅ extent <- `<pages>`
- ✅ classification authority="ssif" <- `<nationalCategories><subject><subjectCode>`
- ✅ subject authority="diva" <- `<researchSubjects>`
- ✅ subject authority="sdg" <- `<sustainableDevelopments>` (värden som inte är giltiga för valideringen behöver uppdateras)
- ✅ identifier type="isbn"
- ✅ identifier type="doi"
- identifier type="ismn"
  ```xml
    <ismnNumbers>
      <ismn>
        <number>978-91-506-2649-0</number>
        <type>print</type>
      </ismn>
      <ismn>
        <number>978-92-893-7379-1</number>
        <type>electronic</type>
      </ismn>
      <ismn>
        <number>978-92-893-7380-7</number>
      </ismn>
    </ismnNumbers>
  ```
- ✅ identifier type="archiveNumber"> <- `<archiveNumber>`
- identifier type="openAlex" (NY)
- ✅ identifier type="se-libr"
- ✅ identifier type="localId"
- ✅ identifier type type="pmid"
- ✅ identifier type type="wos"
- ✅ identifier type type="scopus"
- ✅ location <- `<urls><url>` (openAccess behöver hanteras)
- location displayLabel="orderLink"
  ```xml
  <publicationOrder>
    <orderProfileId>OrderProfile-4</orderProfileId>  (Kolla upp i höst, ärgeneriska texter i Classic)
    <orderURL>https://liu.powerinit.com/Modules/Prepri/Public/Login.aspx?c=3</orderURL> Troligen
    <orderLink>true</orderLink>
    <validFrom>2021-02-04T06:34:00.000+01:00</validFrom>
    <parameters/>
  </publicationOrder>
  ```
- ✅note type="external" <- `<note>`
- ✅ relatedItem type="series" <- `<seriesInfo>` och `<uncontrolledSeriesInfo>`
  - ✅ series <- `<seriesInfo>`
  - ✅ titleInfo/mainTitle <- `uncontrolledSeriesInfo/series/seriesNameUncontrolled`
  - ✅ identifier type="issn" displayLabel="pissn" <- `uncontrolledSeriesInfo/series/issn`
  - ✅ identifier type="issn" displayLabel="eissn" <- `uncontrolledSeriesInfo/series/eissn`
  - ✅ partNumber <- `uncontrolledSeriesInfo/numberInSeries` (?)
  - ❌ No mapping: `uncontrolledSeriesInfos/seriesAlternativeTitles, subjects, relationships`
- relatedItem type="researchData" (NY)
- relatedItem type="project" <- `<projects>`
- relatedItem type="initiative" (NY)
- accessCondition authority="kb.se" (NY)
- localGenericMarkup (NY)
- adminInfo
  - ✅ failed <- `<failed>`
  - ✅ reviewed <- `<reviewed>`
  - ✅ note type="internal" <- `<internalNote>`

## Behövs för Samlingsverk Update

- attachment
  - `<agreementAccepted>` - kanske inte sparas?

## Behövs ej för Sammlingsverk

- genre type="subcategory" <- `<subType>`
- note type="publicationStatus" <- `<publicationStatus>` (behöver mappas om till värden i Cora)
- typeOfResource <- `<mediaInformation>` från `get_mediatype`
- type <- `<mediaInformation>`
- material <- `<mediaInformation>`
- technique <- `<mediaInformation>`
- size <- `<mediaInformation>`
- duration <- `<mediaInformation>`
- physicalDescription <- `<mediaInformation>`
- dateOther type="patent" <- `<patentDate>`
- imprint (Gäller bara UU)
- ✅ identifier type="patentNumber"
- ✅ identifier type="isrn"
- academicSemester <- `<academicTerm>`
- studentDegree <- `<studentDegrees>`
  - degreeLevel <- `studentDegree/thesisLevel/thesisLevelCode`
  - universityPoints <- `studentDegree/universityPoiunts/hp`
  - course <- link to diva-course by oldId: `studentDegree/undergraduateSubject/subjectId`
  - programme <- link to diva-programme by oldId: `studentDegree/educationalProgramme/subjectId`
- externalCollaboration <- `<externalCooperation>`
- degreeGrantingInstitution type="corporate" <- `<defence><grantingInstitution>`
- supervisor type="personal" <- `<supervisors><person>`
- examiner type="personal" <- `<examiners><person>`
- opponent type="personal" <- `<opponents><person>`
- presentation <- `<defence>` (Kolla om både presentation och defence behövs)
- defence <- `<defence>`
- relatedItem type="journal" <- `<journal>`
- relatedItem type="book" <- `<bookTitle>` och `<bookEdition>` <- `<statmentOfResponsibility>` som barnelement i Cora
- relatedItem type="conferencePublication" <- `<proceedingsTitle>` och `<proceedingsEditor>` <- `<statmentOfResponsibility>` som barnelement i Cora
- relatedItem type="conference" <- `<conference>`
- relatedItem type="funder" <- `<funderInfos><funderId><projectNumber>`
- related (NY)
- related type="retracted" (NY)
- related type="constituent" (länkade avhandligar)
- note type="statementOfResponsibility

## Behöver mer information för att migrera

- `<hidden>` - Om true visas posten ej i sökgränssnittet. Och måste sökas fram med särskild flagga. kommer behöva hanteras vid migrering. Kanske blir visibility: unpublished?
- `<publicationChannel>` - Används för konstnärlig output. Metadata ej klar i Cora.

## Taggar ej i Cora

- `<reviewedBefore>`
- `<distributor>`
- `<distributorAsDist>`
- `<formatElectronic>`
- `<formatPrint>`
- `<canOrderOnline>`
- `<migrated>`
- `<version>`
- `<registratedDuplicate>`
- `<importDuplicate>`
- `<categories>`
