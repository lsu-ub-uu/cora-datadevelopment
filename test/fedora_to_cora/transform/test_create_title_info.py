import pytest
from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_title_info import _create_title_info


source_record = ET.fromstring(
    """
    <publication>
        <originalPublicationTitle>
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            <subTitle></subTitle>
            <language>
                <languageCode3>eng</languageCode3>
                <languageCode2>en</languageCode2>
                <languageNames>
                    <languageName>
                    <languageNameId>1145</languageNameId>
                    <locale>en</locale>
                    <languageName>English</languageName>
                    </languageName>
                    <languageName>
                    <languageNameId>10120</languageNameId>
                    <locale>no</locale>
                    <languageName>engelsk</languageName>
                    </languageName>
                    <languageName>
                    <languageNameId>1144</languageNameId>
                    <locale>sv</locale>
                    <languageName>Engelska</languageName>
                    </languageName>
                </languageNames>
                <showsOnList>true</showsOnList>
            </language>
        </originalPublicationTitle>
    </publication>
"""
)


def test_create_title_info():
    title_info = _create_title_info(source_record)
    assert title_info.tag == "titleInfo"
    assert title_info.attrib["lang"] == "eng"

    title = title_info.find("title")
    assert title is not None
    assert title.text == "Bulletin of the Museum of Far Eastern Antiquities (BMFEA)"
    assert title_info.find("subTitle") is None


def test_create_title_info_with_subtitle():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
                <subTitle>subtitle</subTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    title_info = _create_title_info(source_record_with_subtitle)
    assert title_info.tag == "titleInfo"
    assert title_info.attrib["lang"] == "eng"

    title = title_info.find("title")
    assert title is not None
    assert title.text == "Bulletin of the Museum of Far Eastern Antiquities (BMFEA)"
    sub_title = title_info.find("subTitle")
    assert sub_title is not None
    assert sub_title.text == "subtitle"


def test_create_title_info_raises_error_on_missing_title():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    pytest.raises(AssertionError, _create_title_info, source_record_with_subtitle)


def test_create_title_info_raises_error_on_missing_language_code3():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            </originalPublicationTitle>
        </publication>
    """
    )

    pytest.raises(AssertionError, _create_title_info, source_record_with_subtitle)

    source_record = ET.fromstring(
        """                          
        <publication>
          <contentType>
            <contentTypeId>50</contentTypeId>
            <contentTypeCode>refereed</contentTypeCode>
            <contentTypeNames>
              <contentTypeName>
                <contentTypeNameId>106</contentTypeNameId>
                <locale>no</locale>
                <contentTypeName>Fagfellevurdert</contentTypeName>
              </contentTypeName>
              <contentTypeName>
                <contentTypeNameId>101</contentTypeNameId>
                <locale>sv</locale>
                <contentTypeName>Refereegranskat</contentTypeName>
              </contentTypeName>
              <contentTypeName>
                <contentTypeNameId>100</contentTypeNameId>
                <locale>en</locale>
                <contentTypeName>Refereed</contentTypeName>
              </contentTypeName>
            </contentTypeNames>
            <sortOrder>1</sortOrder>
          </contentType>
          <publicationType>
            <publicationTypeId>63</publicationTypeId>
            <publicationTypeCode>collection</publicationTypeCode>
            <openUrlType>book</openUrlType>
            <publicationTypeNames>
              <publicationTypeName>
                <publicationTypeNameId>226</publicationTypeNameId>
                <locale>sv</locale>
                <publicationTypeName>Samlingsverk (redaktörskap)</publicationTypeName>
              </publicationTypeName>
              <publicationTypeName>
                <publicationTypeNameId>247</publicationTypeNameId>
                <locale>no</locale>
                <publicationTypeName>Collection/Antologi</publicationTypeName>
              </publicationTypeName>
              <publicationTypeName>
                <publicationTypeNameId>227</publicationTypeNameId>
                <locale>en</locale>
                <publicationTypeName>Collection (editor)</publicationTypeName>
              </publicationTypeName>
            </publicationTypeNames>
            <roles></roles>
            <comprehensiveSummary>false</comprehensiveSummary>
            <domainAdminOnly>false</domainAdminOnly>
          </publicationType>
          <pid>diva2:1781879</pid>
          <administrativeInfo>
            <domain>varldskulturmuseerna</domain>
            <creatorInfo>
              <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
              <ip>130.242.56.66</ip>
              <name>Helena Rundkrantz</name>
              <date>2023-07-11T13:51:52.940+02:00</date>
              <userType>DOMAINADMIN</userType>
              <userAction>CREATED</userAction>
            </creatorInfo>
            <updaters>
              <userInformation>
                <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
                <ip>130.242.56.66</ip>
                <name>Helena Rundkrantz</name>
                <date>2023-07-11T13:51:52.877+02:00</date>
                <userType>DOMAINADMIN</userType>
                <userAction>AUTOPUBLISHED</userAction>
              </userInformation>
              <userInformation>
                <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
                <ip>130.242.56.66</ip>
                <name>Helena Rundkrantz</name>
                <date>2023-07-11T14:00:43.925+02:00</date>
                <userType>DOMAINADMIN</userType>
                <userAction>UPDATED</userAction>
              </userInformation>
              <userInformation>
                <userId>helena.rundkrantz@varldskulturmuseerna.se</userId>
                <ip>130.242.56.66</ip>
                <name>Helena Rundkrantz</name>
                <date>2023-08-04T14:38:12.593+02:00</date>
                <userType>DOMAINADMIN</userType>
                <userAction>UPDATED</userAction>
              </userInformation>
            </updaters>
            <createdDate>2023-07-11T13:51:52.940+02:00</createdDate>
            <updatedDate>2023-08-04T14:38:12.593+02:00</updatedDate>
          </administrativeInfo>
          <publicationDate>2023-07-11T13:51:00.000+02:00</publicationDate>
          <editors>
            <person>
              <firstName>Östasiatiska museet</firstName>
              <lastName>Östasiatiska museet</lastName>
              <organisations>
                <organisation>
                  <organisationId>885801</organisationId>
                  <organisationType>
                    <organisationTypeId>64</organisationTypeId>
                    <organisationTypeCode>authority</organisationTypeCode>
                    <organisationTypeNames>
                      <organisationTypeName>
                        <organisationTypeNameId>1930</organisationTypeNameId>
                        <locale>sv</locale>
                        <organisationTypeName>Myndighet</organisationTypeName>
                      </organisationTypeName>
                      <organisationTypeName>
                        <organisationTypeNameId>1931</organisationTypeNameId>
                        <locale>en</locale>
                        <organisationTypeName>Authority</organisationTypeName>
                      </organisationTypeName>
                    </organisationTypeNames>
                  </organisationType>
                  <organisationName>
                    <name>Världskulturmuseerna</name>
                    <locale>sv</locale>
                  </organisationName>
                  <organisationHomepage>https://www.varldskulturmuseerna.se/</organisationHomepage>
                  <domain>varldskulturmuseerna</domain>
                  <organisationNumber>202100-5075</organisationNumber>
                  <organisationAlternativeNames>
                    <organisationName>
                      <organisationNameId>84801</organisationNameId>
                      <locale>en</locale>
                      <organisationName>National Museums of World Culture</organisationName>
                    </organisationName>
                  </organisationAlternativeNames>
                  <organisationContacts></organisationContacts>
                  <organisationParents></organisationParents>
                  <organisationPredecessors></organisationPredecessors>
                  <organisationPredecessorDescriptions></organisationPredecessorDescriptions>
                  <controlled>true</controlled>
                  <notEligible>false</notEligible>
                  <showInPortal>true</showInPortal>
                  <showInDefence>false</showInDefence>
                  <topLevel>true</topLevel>
                </organisation>
                <organisation>
                  <organisationContacts></organisationContacts>
                  <organisationPredecessors></organisationPredecessors>
                  <organisationPredecessorDescriptions></organisationPredecessorDescriptions>
                  <organisationNameUncontrolled>Statens museer för Världskultur</organisationNameUncontrolled>
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
          </editors>
          <originalPublicationTitle>
            <title>Bulletin of the Museum of Far Eastern Antiquities, Vol 76</title>
            <subTitle></subTitle>
            <language>
              <languageCode3>eng</languageCode3>
              <languageCode2>en</languageCode2>
              <languageNames>
                <languageName>
                  <languageNameId>1145</languageNameId>
                  <locale>en</locale>
                  <languageName>English</languageName>
                </languageName>
                <languageName>
                  <languageNameId>10120</languageNameId>
                  <locale>no</locale>
                  <languageName>engelsk</languageName>
                </languageName>
                <languageName>
                  <languageNameId>1144</languageNameId>
                  <locale>sv</locale>
                  <languageName>Engelska</languageName>
                </languageName>
              </languageNames>
              <showsOnList>true</showsOnList>
            </language>
          </originalPublicationTitle>
          <seriesInfos>
            <seriesInfo>
              <series>
                <seriesId>21250</seriesId>
                <seriesTitle>
                  <titleId>65300</titleId>
                  <mainTitle>Bulletin of the Museum of Far Eastern Antiquities</mainTitle>
                  <locale>sv</locale>
                </seriesTitle>
                <seriesAlternativeTitles></seriesAlternativeTitles>
                <issn>0081-5691</issn>
                <subjects></subjects>
                <relationships></relationships>
                <domain>varldskulturmuseerna</domain>
                <controlled>true</controlled>
              </series>
              <numberInSeries>76</numberInSeries>
            </seriesInfo>
          </seriesInfos>
          <dateIssued>2004</dateIssued>
          <pages>189</pages>
          <distributor>
            <organisationAlternativeNames></organisationAlternativeNames>
            <organisationContacts></organisationContacts>
            <organisationParents></organisationParents>
            <organisationPredecessors></organisationPredecessors>
            <organisationPredecessorDescriptions></organisationPredecessorDescriptions>
            <controlled>true</controlled>
            <notEligible>false</notEligible>
            <showInPortal>false</showInPortal>
            <showInDefence>false</showInDefence>
            <topLevel>false</topLevel>
          </distributor>
          <publisher>
            <city>Värnamo</city>
          </publisher>
          <nbn>urn:nbn:se:varldskulturmuseerna:diva-16</nbn>
          <oai>oai:DiVA.org:varldskulturmuseerna-16</oai>
          <identifiers></identifiers>
          <categories></categories>
          <nationalCategories>
            <subject>
              <subjectId>11803</subjectId>
              <subjectType>
                <subjectTypeId>57</subjectTypeId>
                <subjectTypeCode>hsv</subjectTypeCode>
                <subjectTypeNames>
                  <subjectTypeName>
                    <subjectTypeNameId>3723</subjectTypeNameId>
                    <locale>no</locale>
                    <subjectTypeName>HSV kategorier</subjectTypeName>
                  </subjectTypeName>
                  <subjectTypeName>
                    <subjectTypeNameId>3722</subjectTypeNameId>
                    <locale>en</locale>
                    <subjectTypeName>HSV categories</subjectTypeName>
                  </subjectTypeName>
                  <subjectTypeName>
                    <subjectTypeNameId>3721</subjectTypeNameId>
                    <locale>sv</locale>
                    <subjectTypeName>HSV kategorier</subjectTypeName>
                  </subjectTypeName>
                </subjectTypeNames>
              </subjectType>
              <subjectNames>
                <subjectName>
                  <subjectNameId>28756</subjectNameId>
                  <locale>sv</locale>
                  <subjectName>Övrig annan humaniora</subjectName>
                </subjectName>
                <subjectName>
                  <subjectNameId>28757</subjectNameId>
                  <locale>en</locale>
                  <subjectName>Other Humanities not elsewhere specified</subjectName>
                </subjectName>
              </subjectNames>
              <subjectCode>60599</subjectCode>
              <parents>
                <subject>
                  <subjectId>11799</subjectId>
                  <subjectType>
                    <subjectTypeId>57</subjectTypeId>
                    <subjectTypeCode>hsv</subjectTypeCode>
                    <subjectTypeNames>
                      <subjectTypeName>
                        <subjectTypeNameId>3723</subjectTypeNameId>
                        <locale>no</locale>
                        <subjectTypeName>HSV kategorier</subjectTypeName>
                      </subjectTypeName>
                      <subjectTypeName>
                        <subjectTypeNameId>3722</subjectTypeNameId>
                        <locale>en</locale>
                        <subjectTypeName>HSV categories</subjectTypeName>
                      </subjectTypeName>
                      <subjectTypeName>
                        <subjectTypeNameId>3721</subjectTypeNameId>
                        <locale>sv</locale>
                        <subjectTypeName>HSV kategorier</subjectTypeName>
                      </subjectTypeName>
                    </subjectTypeNames>
                  </subjectType>
                  <subjectNames>
                    <subjectName>
                      <subjectNameId>28748</subjectNameId>
                      <locale>sv</locale>
                      <subjectName>Annan humaniora</subjectName>
                    </subjectName>
                    <subjectName>
                      <subjectNameId>28749</subjectNameId>
                      <locale>en</locale>
                      <subjectName>Other Humanities</subjectName>
                    </subjectName>
                  </subjectNames>
                  <subjectCode>605</subjectCode>
                  <parents>
                    <subject>
                      <subjectId>11772</subjectId>
                      <subjectType>
                        <subjectTypeId>57</subjectTypeId>
                        <subjectTypeCode>hsv</subjectTypeCode>
                        <subjectTypeNames>
                          <subjectTypeName>
                            <subjectTypeNameId>3723</subjectTypeNameId>
                            <locale>no</locale>
                            <subjectTypeName>HSV kategorier</subjectTypeName>
                          </subjectTypeName>
                          <subjectTypeName>
                            <subjectTypeNameId>3722</subjectTypeNameId>
                            <locale>en</locale>
                            <subjectTypeName>HSV categories</subjectTypeName>
                          </subjectTypeName>
                          <subjectTypeName>
                            <subjectTypeNameId>3721</subjectTypeNameId>
                            <locale>sv</locale>
                            <subjectTypeName>HSV kategorier</subjectTypeName>
                          </subjectTypeName>
                        </subjectTypeNames>
                      </subjectType>
                      <subjectNames>
                        <subjectName>
                          <subjectNameId>28694</subjectNameId>
                          <locale>sv</locale>
                          <subjectName>Humaniora och konst</subjectName>    
                    </subjectName>
                        <subjectName>
                          <subjectNameId>28695</subjectNameId>
                          <locale>en</locale>
                          <subjectName>Humanities and the Arts</subjectName>
                        </subjectName>
                      </subjectNames>
                      <subjectCode>6</subjectCode>
                      <parents></parents>
                      <predecessors></predecessors>
                      <domain>diva</domain>
                      <notEligible>false</notEligible>
                      <organisations></organisations>
                    </subject>
                  </parents>
                  <predecessors></predecessors>
                  <domain>diva</domain>
                  <notEligible>false</notEligible>
                  <organisations></organisations>
                </subject>
              </parents>
              <predecessors></predecessors>
              <domain>diva</domain>
              <notEligible>false</notEligible>
              <organisations></organisations>
            </subject>
          </nationalCategories>
          <researchSubjects>
            <subject>
              <subjectId>40103</subjectId>
              <subjectType>
                <subjectTypeId>53</subjectTypeId>
                <subjectTypeCode>researchSubject</subjectTypeCode>
                <subjectTypeNames>
                  <subjectTypeName>
                    <subjectTypeNameId>3711</subjectTypeNameId>
                    <locale>no</locale>
                    <subjectTypeName>Research subject</subjectTypeName>
                  </subjectTypeName>
                  <subjectTypeName>
                    <subjectTypeNameId>3710</subjectTypeNameId>
                    <locale>en</locale>
                    <subjectTypeName>Research subject</subjectTypeName>
                  </subjectTypeName>
                  <subjectTypeName>
                    <subjectTypeNameId>3709</subjectTypeNameId>
                    <locale>sv</locale>
                    <subjectTypeName>Forskningsämne</subjectTypeName>
                  </subjectTypeName>
                </subjectTypeNames>
              </subjectType>
              <subjectNames>
                <subjectName>
                  <subjectNameId>86107</subjectNameId>
                  <locale>sv</locale>
                  <subjectName>Digital humaniora</subjectName>
                </subjectName>
                <subjectName>
                  <subjectNameId>86106</subjectNameId>
                  <locale>en</locale>
                  <subjectName>Digital humaniora</subjectName>
                </subjectName>
              </subjectNames>
              <parents></parents>
              <predecessors></predecessors>
              <domain>varldskulturmuseerna</domain>
              <notEligible>false</notEligible>
              <organisations></organisations>
            </subject>
          </researchSubjects>
          <note></note>
          <internalNote></internalNote>
          <attachments class="tree-set">
            <no-comparator></no-comparator>
            <attachment>
              <mimeType>
                <mimeTypeId>62</mimeTypeId>
                <mimeTypeName>application/zip</mimeTypeName>
                <fileSuffix>zip</fileSuffix>
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
              <fileSize>17452789</fileSize>
              <selectedFileName>fulltext</selectedFileName>
              <path>4bcb7d8f7deec5f8931a8ea4da02/Bulletin-No76_(BMFEA).zip</path>
              <checksums>
                <checksum>
                  <type>SHA512</type>
                  <digest>0e3fb8ff48a04cd44b7e3776c425d5692ee0714abe640d2c23f0507a6c39b2458e1a5f44c7a3f6183616ec2c86353890653d7fd9f7d34940856858f5eb72777b</digest>
                </checksum>
              </checksums>
              <order>0</order>
              <uploadDate>2023-07-11T13:51:53.594+02:00</uploadDate>
              <asyncUpload>false</asyncUpload>
              <availableFrom>2023-07-11T13:51:53.041+02:00</availableFrom>
              <deleteDate>2023-08-04T14:38:11.987+02:00</deleteDate>
              <onHold>false</onHold>
              <deleted>true</deleted>
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
              <fileName>FULLTEXT02</fileName>
              <fileSize>18634020</fileSize>
              <selectedFileName>fulltext</selectedFileName>
              <path>0857584da3b6114e3c33819c365b/bulletin-no76_bmfea.pdf</path>
              <checksums>
                <checksum>
                  <type>SHA512</type>
                  <digest>00dbe709af6d5bfc00801a77bfff66e8b2259343386cb5f8e0c2eb02c90d216ee38a6f6a92d86cb814603e5a67815e05550f37a61abd983ac4f4705472a6a4ff</digest>
                </checksum>
              </checksums>
              <order>1</order>
              <uploadDate>2023-08-04T14:38:12.543+02:00</uploadDate>
              <asyncUpload>false</asyncUpload>
              <availableFrom>2023-08-04T14:38:11.862+02:00</availableFrom>
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
          <distributorAsDist>
            <distributorNames></distributorNames>
          </distributorAsDist>
          <agreementAccepted>true</agreementAccepted>
          <reviewed>false</reviewed>
          <reviewedBefore>false</reviewedBefore>
          <migrated>false</migrated>
          <importDuplicate>false</importDuplicate>
          <registratedDuplicate>false</registratedDuplicate>
          <artisticWork>false</artisticWork>
          <failed>false</failed>
          <hidden>false</hidden>
          <publicationOrder>
            <orderLink>false</orderLink>
            <parameters></parameters>
          </publicationOrder>
          <canOrderOnline>false</canOrderOnline>
          <publicationChannel></publicationChannel>
        </publication>
        """
    )
    title_info = _create_title_info(source_record)
    assert title_info.tag == "titleInfo"
    assert title_info.attrib["lang"] == "eng"
