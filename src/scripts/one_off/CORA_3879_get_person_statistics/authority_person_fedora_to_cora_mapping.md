| Classic | Cora |
| -------- | ------- |
| authorityPerson/defaultName/firstName | person/authority/name{type:personal}/namePart{type:given} |
| authorityPerson/defaultName/lastname | person/authority/name{type:personal}/namePart{type:family} |
| authorityPerson/defaultName/addition | person/authority/name{type:personal}/namePart{type:termsOfAddress} |
| N/A | person/authority/name{type:personal}/namePart{type:date} |
| authorityPerson/defaultName/number ** | N/A |
| authorityPerson/alternativeNames/nameForm*/firstName | person/authority/name{type:personal}/namePart{type:given} |
| authorityPerson/alternativeNames/nameForm*/lastname | person/authority/name{type:personal}/namePart{type:family} |
| authorityPerson/alternativeNames/nameForm*/addition | N/A |
| authorityPerson/alternativeNames/nameForm*/number | N/A |
| authorityPerson/affiliations/affiliation*/active | N/A |
| authorityPerson/affiliations/affiliation*/alternativeName | N/A |
| authorityPerson/affiliations/affiliation*/domain | N/A |
| authorityPerson/affiliations/affiliation*/from | person/affiliation*/startDate/year |
| authorityPerson/affiliations/affiliation*/name | person/affiliation*/namePart † |
| authorityPerson/affiliations/affiliation*/organisationId | person/affiliation*/organisation/linkedRecordId ‡ |
| authorityPerson/affiliations/affiliation*/organisationNumber | N/A |
| authorityPerson/affiliations/affiliation*/parents | N/A |
| N/A | person/affiliation*/startDate/month |
| N/A | person/affiliation*/startDate/day |
| N/A | person/affiliation*/identifier{type:ror} |
| authorityPerson/biographies/entry* | person/note{type:biographical}* ⹋ |
| authorityPerson/birthYear | N/A |
| authorityPerson/deathYear | N/A |
| authorityPerson/duplicateCheckDate | N/A |
| authorityPerson/email | person/email* |
| authorityPerson/identifiers/identifier*/domain | N/A  |
| authorityPerson/identifiers/identifier*/from ** | N/A|
| authorityPerson/identifiers/identifier*[type=ORCID]/value | person/nameIdentifier{type:orcid}* |
| authorityPerson/identifiers/identifier*[type=VIAF]/value | person/nameIdentifier{type:viaf}* |
| authorityPerson/identifiers/identifier*[type=LIBRIS]/value | person/nameIdentifier {type:se-libr}* |
| authorityPerson/identifiers/identifier*[type=LOCAL]/domain | person/localId*/permissionUnit/linkedRecordId ‡  |
| authorityPerson/identifiers/identifier*[type=LOCAL]/value | person/localId*/nameIdentifier type:{localId} |
| N/A | person/nameIdentifier{type:openAlex } |
| N/A | person/nameIdentifier{type:scopus} |
| N/A | person/nameIdentifier{type:wos} |
| N/A | person/nameIdentifier{type:googleScholar} |
| authorityPerson/identifiers/identifier*/until | N/A |
| authorityPerson/identifiers/identifier*/from ** | N/A |
| authorityPerson/publicRecord | N/A |
| authorityPerson/type | N/A |
| authorityPerson/urls/url*/label | person/location*/displayLabel |
| authorityPerson/urls/url*/url | person/location*/url |
| authorityPerson/recordInfo | N/A |
| authorityPerson/pid | person/recordInfo/oldId |
| authorityPerson/recordDeleted | person/recordInfo/inTrashBin (?) |





* Repeating element

** Always empty


† Only set if affiliation has no organisationId

‡ The corresponding cora record id

⹋ Entries look like: `<entry><string>eng</string><string>&lt;p&gt;Some text&lt;/p&gt;</string>`. Need to strip HTML and map to `<note type="biographical" lang="eng">Some text</note>`

(?) Unsure
