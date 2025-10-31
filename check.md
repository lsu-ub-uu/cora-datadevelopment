- keywords
  <list>
  <string>keywords</string>
  <string>several words</string>
  </list>

i ny modellen så så blir det en kommaseparead lista

- viaf, libris tar inte med i ny modellen på person

- jounals, kolla för skräpdata

- location displayLabel="orderLink" (Kolla upp orderProfileId i höst, är generiska texter i Classic för displayLabel, url från orderURL)

- `hidden` - Om true visas posten ej i sökgränssnittet. Och måste sökas fram med särskild flagga. kommer behöva hanteras vid migrering. Kanske blir visibility: unpublished?
- `publicationChannel` - Används för konstnärlig output. Metadata ej klar i Cora.

- attachment

  - `agreementAccepted` - Ska det verkligen vara bara frontend? hur gör api?

- url displayLabel bara ett språk?

Marcus:

- hur hanterar vi andra värden i collectionVars?
