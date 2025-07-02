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
  - ✅ validationType ← `<publicationType><publicationTypeId>`
  - ✅ permissionUnit ← domain
  - ✅ oldId ← `<pid>`
  - ✅ visibility ← `<administrativeInfo><updaters><userInformation><userAction>`
  - ✅ genre type="contentType" ← `<contentType><contentTypeCode>`
- ✅ titleInfo type="main" ← `<originalPublicationTitle>`
- ✅ subject ← `<keyWords>`
- ✅ genre type="outputType" (valideringstyp) ← `<publicationType>` via `get_validation_type_by_publication_typ`
- ✅ language ← `<originalPuoriblicationTitle><language>`
- ✅ artisticWork type="outputType" ← `<artisticWork>`
- ✅ titleInfo type="alternative" ← `<alternativePublicationTitles>`
- ✅ name type="personal" ←

  ```xml
  <authors><person>
  <editors><person>
  <examiners><person>
  <supervisors><person>
  <opponents><person>
  ```

- ❌ name type="corporate" ← skipped
- ✅ note type="creatorCount"
- ✅ abstract ← `<abstracts><abstract>`

- originInfo
  - ✅ dateIssued ← `<publicationDate>`
  - copyrightDate
  - dateOther type="online"
  - agent
  - place
  - edition
- extent ← Verkets fysiska omfattning
- classification authority="ssif" ← `<nationalCategories>`
- subject authority="diva" ← `<researchSubjects>`
- subject authority="sdg" ← `<sustainableDevelopments>` (behöver extra jobb)

- ✅ identifier type="isbn"
- ✅ identifier type="doi"
- identifier type="ismn"
- identifier type="archiveNumber"
- identifier type="openAlex" (NY)
- ✅ identifier type="se-libr"
- identifier type="localId"
- identifiertype type="pmid"
- identifiertype type="wos"`<artisticWork>false</artisticWork>`
- identifiertype type="scopus"
- location ← `<urls><url>`
- location displayLabel="orderLink"
  ```xml
  <publicationOrder>
    <orderProfileId>OrderProfile-4</orderProfileId>
    <orderURL>https://liu.powerinit.com/Modules/Prepri/Public/Login.aspx?c=3</orderURL> Troligen
    <orderLink>true</orderLink>
    <validFrom>2021-02-04T06:34:00.000+01:00</validFrom>
    <parameters/>
  </publicationOrder>
  ```
- note type="external" ← `<note>`
- relatedItem type="series" ← `<seriesInfo>`
- relatedItem type="researchData" (NY)
- relatedItem type="project"
- relatedItem type="initiative"

- relatedItem type="retracted | constituent | thesis"
- accessCondition authority="kb.se"
- localGenericMarkup (NY)
- admin
  - ✅ reviewed
  - note type="internal" ← `<internalNote>`

## Behövs för Sammlingsverk Update

- attachment
  - `<agreementAccepted>` - kanske inte sparas?

## Behövs ej för Sammlingsverk

- genre type="subcategory"
- note type="publicationStatus"
- typeOfResource
- type
- material
- technique
- size
- duration
- physicalDescription
- dateOther type="patent"
- imprint
- identifier type="patentNumber"
- ✅ identifier type="isrn"
- academicSemester
- studentDegree
- externalCollaboration
- degreeGrantingInstitution type="corporate"
- supervisor type="personal"
- examiner type="personal"
- opponent type="personal"
- presentation
- defence
- relatedItem type="journal"
- relatedItem type="book"
- relatedItem type="conferencePublication"
- relatedItem type="conference"
- relatedItem type="funder" <- `<funderInfos><funderId><projectNumber>`
- relatedItem type="retracted"
- relatedItem type="constituent"
- failed

## Okänt:

- `<hidden>` - kommer behöva hanteras vid migrering
- `<publicationChannel>` - kommer behövas

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
