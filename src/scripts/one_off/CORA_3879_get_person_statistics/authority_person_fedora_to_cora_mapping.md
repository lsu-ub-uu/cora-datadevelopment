| Classic (authorityPerson)                    | Cora (diva-person)                                           |
| -------------------------------------------- | ------------------------------------------------------------ |
| defaultName/firstName                        | authority/name{type:personal}/namePart{type:given}           |
| defaultName/lastname                         | authority/name{type:personal}/namePart{type:family}          |
| defaultName/addition                         | authority/name{type:personal}/namePart{type:termsOfAddress}  |
| defaultName/number **                        | N/A                                                          |
| birthYear                                    | authority/name{type:personal}/namePart{type:date} ⁂         |
| deathYear                                    | authority/name{type:personal}/namePart{type:date} ⁂         |
| alternativeNames/nameForm*/firstName         | variant*/name{type:personal}/namePart{type:given}            |
| alternativeNames/nameForm*/lastname          | variant*/name{type:personal}/namePart{type:family}           |
| alternativeNames/nameForm*/addition          | N/A                                                          |
| alternativeNames/nameForm*/number**          | N/A                                                          |
| affiliations/affiliation*/active             | N/A                                                          |
| affiliations/affiliation*/alternativeName    | N/A                                                          |
| affiliations/affiliation*/domain             | N/A                                                          |
| affiliations/affiliation*/from               | affiliation*/startDate/year                                  |
| N/A                                          | affiliation*/startDate/month                                 |
| N/A                                          | affiliation*/startDate/day                                   |
| affiliations/affiliation*/until              | affiliation*/endDate/year                                    |
| N/A                                          | affiliation*/endDate/month                                   |
| N/A                                          | affiliation*/endDate/day                                     |
| affiliations/affiliation*/name               | affiliation*/namePart †                                      |
| affiliations/affiliation*/organisationId     | affiliation*/organisation ‡                                  |
| affiliations/affiliation*/organisationNumber | N/A                                                          |
| affiliations/affiliation*/parents            | N/A                                                          |
| N/A                                          | affiliation*/identifier{type:ror}                            |
| N/A                                          | affiliation*/country                                         |
| N/A                                          | affiliation*/description                                     |
| biographies/entry*                           | note{type:biographical}* ⹋                                   |
| duplicateCheckDate                           | N/A                                                          |
| email                                        | email*                                                       |
| identifiers/identifier*/domain               | N/A                                                          |
| identifiers/identifier*/from**               | N/A                                                          |
| identifiers/identifier*/until**              | N/A                                                          |
| identifiers/identifier*[type=ORCID]/value    | nameIdentifier{type:orcid}*                                  |
| identifiers/identifier*[type=VIAF]/value     | nameIdentifier{type:viaf}*                                   |
| identifiers/identifier*[type=LIBRIS]/value   | nameIdentifier {type:se-libr}*                               |
| identifiers/identifier*[type=LOCAL]/domain   | localId*/permissionUnit ‡                                    |
| identifiers/identifier*[type=LOCAL]/value    | localId*/nameIdentifier{type:localId}                        |
| N/A                                          | nameIdentifier{type:openAlex}*                               |
| N/A                                          | nameIdentifier{type:scopus}*                                 |
| N/A                                          | nameIdentifier{type:wos}*                                    |
| N/A                                          | nameIdentifier{type:googleScholar}*                          |
| identifiers/identifier*/until                | N/A                                                          |
| publicRecord                                 | N/A                                                          |
| type                                         | N/A                                                          |
| urls/url*/label                              | location*/displayLabel                                       |
| urls/url*/url                                | location*/url                                                |
| recordInfo/events/event*/ip                  | N/A                                                          |
| recordInfo/events/event*/name                | N/A                                                          |
| recordInfo/events/event*/timestamp           | N/A                                                          |
| recordInfo/events/event*/type                | N/A                                                          |
| recordInfo/events/event*/userId              | N/A                                                          |
| recordInfo/recordDeleted                     | N/A (do not sync)                                            |
| N/A (do not sync)                            | recordInfo/inTrashBin                                        |
| N/A                                          | recordInfo/id                                                |
| N/A                                          | recordInfo/type                                              |
| N/A                                          | recordInfo/validationType                                    |
| N/A                                          | recordInfo/dataDivider                                       |
| N/A                                          | recordInfo/createdBy                                         |
| N/A                                          | recordInfo/tsCreated                                         |
| N/A                                          | recordInfo/updated*/updatedBy                                |
| N/A                                          | recordInfo/updated*/tsUpdated                                |
| pid                                          | recordInfo/oldId                                             |       


\* Repeating element

** Always empty

⁂ Birth year and death year are combined to one field in Cora model as follows:  Only birth year: "1930", Only death year: "-2010", Birth+death year: "1930-2010".

† Only set if affiliation has no organisationId

‡ Record link to the corresponding Cora record

⹋ Entries look like: `<entry><string>eng</string><string>&lt;p&gt;Some text&lt;/p&gt;</string>`. Need to strip HTML and map to `<note type="biographical" lang="eng">Some text</note>`

(?) Unsure
