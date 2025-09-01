import xml.etree.ElementTree as ET
from fabric import Connection


LOCAL_PORT = 8080

# REMOTE_HOST = "diva-node4"
# REMOTE_PORT = 8080
# SOLR_SEARCH_URL = f"http://localhost:{LOCAL_PORT}/diva-search/diva/select"

REMOTE_HOST = "diva-node7"
REMOTE_PORT = 8083
SOLR_SEARCH_URL = f"http://localhost:{LOCAL_PORT}/solr-admin/dream/select"


def download_attachments(fedora_publication: ET.Element) -> None:
    pid = fedora_publication.findtext("./pid")

    filenames = []

    for attachment in fedora_publication.findall("./attachments/attachment"):
        filename = attachment.findtext("./fileName")
        if filename:
            filenames.append(filename)

    # With SSH tunnel
    for filename in filenames:
        print(f"Downloading {filename} from {pid}")
        url = f"http://localhost:{LOCAL_PORT}/fedora/get/{pid}/{filename}"
        print(f"URL: {url}")


if __name__ == "__main__":
    publication = ET.fromstring(
        """
<publication>
  <publicationType>
    <publicationTypeId>65</publicationTypeId>
    <publicationTypeCode>studentThesis</publicationTypeCode>
    <openUrlType>book</openUrlType>
    <publicationTypeNames>
      <publicationTypeName>
        <publicationTypeNameId>231</publicationTypeNameId>
        <locale>en</locale>
        <publicationTypeName>Student thesis</publicationTypeName>
      </publicationTypeName>
      <publicationTypeName>
        <publicationTypeNameId>230</publicationTypeNameId>
        <locale>sv</locale>
        <publicationTypeName>Studentuppsats (Examensarbete)</publicationTypeName>
      </publicationTypeName>
      <publicationTypeName>
        <publicationTypeNameId>250</publicationTypeNameId>
        <locale>no</locale>
        <publicationTypeName>Oppgave</publicationTypeName>
      </publicationTypeName>
    </publicationTypeNames>
    <roles></roles>
    <comprehensiveSummary>false</comprehensiveSummary>
    <domainAdminOnly>false</domainAdminOnly>
  </publicationType>
  <pid>diva2:1775040</pid>
  <administrativeInfo>
    <domain>varldskulturmuseerna</domain>
    <creatorInfo>
      <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
      <ip>130.242.56.66</ip>
      <name>Helena Rundkrantz</name>
      <date>2023-06-26T15:44:46.489+02:00</date>
      <userType>DOMAINADMIN</userType>
      <userAction>CREATED</userAction>
    </creatorInfo>
    <updaters>
      <userInformation>
        <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
        <ip>130.242.56.66</ip>
        <name>Helena Rundkrantz</name>
        <date>2023-06-26T15:54:58.129+02:00</date>
        <userType>DOMAINADMIN</userType>
        <userAction>PUBLISHED</userAction>
      </userInformation>
    </updaters>
    <createdDate>2023-06-26T15:44:46.489+02:00</createdDate>
    <updatedDate>2023-06-26T15:54:58.129+02:00</updatedDate>
  </administrativeInfo>
  <publicationDate>2023-06-26T15:54:00.000+02:00</publicationDate>
  <authors>
    <person>
      <firstName>Ylva</firstName>
      <lastName>Johansson Sjögren</lastName>
      <organisations>
        <organisation>
          <organisationContacts></organisationContacts>
          <organisationPredecessors></organisationPredecessors>
          <organisationPredecessorDescriptions></organisationPredecessorDescriptions>
          <organisationNameUncontrolled>Linnéuniversitetet</organisationNameUncontrolled>
          <controlled>false</controlled>
          <notEligible>false</notEligible>
          <showInPortal>false</showInPortal>
          <showInDefence>false</showInDefence>
          <topLevel>false</topLevel>
        </organisation>
      </organisations>
      <identifiers>
        <entry>
          <personIdentifierType>orcid</personIdentifierType>
          <personIdentifier>
            <value></value>
            <type>orcid</type>
          </personIdentifier>
        </entry>
      </identifiers>
    </person>
  </authors>
  <originalPublicationTitle>
    <title>Bildanalyser av Tyra Kleens verk</title>
    <subTitle>En studie över konstnärens tid på Bali och Java och hennes påverkan av danstraditioner och mudras i det konstnärliga skapandet</subTitle>
    <language>
      <languageCode3>swe</languageCode3>
      <languageCode2>sv</languageCode2>
      <languageNames>
        <languageName>
          <languageNameId>10261</languageNameId>
          <locale>no</locale>
          <languageName>svensk</languageName>
        </languageName>
        <languageName>
          <languageNameId>1723</languageNameId>
          <locale>sv</locale>
          <languageName>Svenska</languageName>
        </languageName>
        <languageName>
          <languageNameId>1722</languageNameId>
          <locale>en</locale>
          <languageName>Swedish</languageName>
        </languageName>
      </languageNames>
      <showsOnList>true</showsOnList>
    </language>
  </originalPublicationTitle>
  <dateIssued>2023</dateIssued>
  <pages>53</pages>
  <publisher></publisher>
  <nbn>urn:nbn:se:varldskulturmuseerna:diva-15</nbn>
  <oai>oai:DiVA.org:varldskulturmuseerna-15</oai>
  <identifiers></identifiers>
  <categories></categories>
  <nationalCategories></nationalCategories>
  <researchSubjects></researchSubjects>
  <defence>
    <room></room>
  </defence>
  <note></note>
  <internalNote></internalNote>
  <attachments class="tree-set">
    <no-comparator></no-comparator>
    <attachment>
      <mimeType>
        <mimeTypeId>50</mimeTypeId>
        <mimeTypeName>application/pdf</mimeTypeName>
        <fileSuffix>pdf</fileSuffix>
        <datasetOnly>false</datasetOnly>
      </mimeType>
      <fileLabel>
        <fileLabelId>50</fileLabelId>
        <fileLabelCode>fulltext</fileLabelCode>
        <fileLabelNames>
          <fileLabelName>
            <fileLabelNameId>3674</fileLabelNameId>
            <locale>no</locale>
            <fileLabelName>fulltekst</fileLabelName>
          </fileLabelName>
          <fileLabelName>
            <fileLabelNameId>3651</fileLabelNameId>
            <locale>sv</locale>
            <fileLabelName>fulltext</fileLabelName>
          </fileLabelName>
          <fileLabelName>
            <fileLabelNameId>3650</fileLabelNameId>
            <locale>en</locale>
            <fileLabelName>fulltext</fileLabelName>
          </fileLabelName>
        </fileLabelNames>
      </fileLabel>
      <fileName>FULLTEXT01</fileName>
      <fileSize>3766529</fileSize>
      <selectedFileName>fulltext</selectedFileName>
      <path>7ea516b55d35c07102a26261a2d2/Kandidatuppsats Ylva.slutversion.pdf</path>
      <checksums>
        <checksum>
          <type>SHA512</type>
          <digest>1d032a5febe1ad88e449a7090496912e07ed35953a57262c160ad15e301512b94d1570bd118f5e5599aeaf993faf0ed899b19068ab5e9160c165b063f92337c1</digest>
        </checksum>
      </checksums>
      <order>1</order>
      <uploadDate>2023-06-26T15:44:46.807+02:00</uploadDate>
      <asyncUpload>false</asyncUpload>
      <availableFrom>2023-06-26T15:54:58.129+02:00</availableFrom>
      <onHold>false</onHold>
      <deleted>false</deleted>
      <prePrint>false</prePrint>
      <postPrint>false</postPrint>
      <print>false</print>
      <archiveOnly>false</archiveOnly>
      <printOnDemand>false</printOnDemand>
      <toBePublished>false</toBePublished>
      <toBeArchived>false</toBeArchived>
      <digitized>false</digitized>
      <hasCoverPage>false</hasCoverPage>
    </attachment>
  </attachments>
  <formatElectronic>false</formatElectronic>
  <formatPrint>false</formatPrint>
  <agreementAccepted>true</agreementAccepted>
  <reviewed>true</reviewed>
  <reviewedBefore>true</reviewedBefore>
  <migrated>false</migrated>
  <importDuplicate>false</importDuplicate>
  <registratedDuplicate>false</registratedDuplicate>
  <artisticWork>true</artisticWork>
  <externalCooperation>
    <external>false</external>
    <partners></partners>
  </externalCooperation>
  <failed>false</failed>
  <hidden>false</hidden>
  <publicationOrder>
    <orderLink>false</orderLink>
    <parameters></parameters>
  </publicationOrder>
  <canOrderOnline>false</canOrderOnline>
  <academicTerm>
    <year></year>
  </academicTerm>
</publication>
"""
    )

    download_attachments(publication)
