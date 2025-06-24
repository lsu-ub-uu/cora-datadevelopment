import xml.etree.ElementTree as ET
from fedora_to_cora import create_abstracts
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_abstracts():
    source_record = ET.fromstring(
        """
        <publication>
            <abstracts>
                <abstract>
                    <language>
                        <languageCode3>swe</languageCode3>
                    </language>
                    <text>Lorem ipsum dolor sit amet</text>
                </abstract>
                <abstract>
                    <language>
                        <languageCode3>eng</languageCode3>
                    </language>
                    <text>
                        &lt;p&gt;Another summary, &lt;strong&gt;bold text&lt;/strong&gt;, &lt;em&gt;cursive text,&lt;/em&gt; &lt;sup&gt;to the power of text&lt;/sup&gt;, 
            &lt;sub&gt;subscript text&lt;/sub&gt;&lt;/p&gt;
            &lt;p&gt;A formula: 
            &lt;img src=&quot;http://www.diva-portal.org/cgi-bin/mimetex.cgi?
            %5Cbigcup_%7B2%7D%5E%7B3%5E%7Bb%7Dx%7D%5Cpm&quot; data-classname=&quot;equation&quot; data-title=&quot;&quot; /&gt;&lt;/p&gt;
                    </text>
                    </abstract>
                </abstracts>
        </publication>
        """
    )

    abstracts = create_abstracts(source_record)

    assert_equal_for_xml_and_xml_string(
        abstracts[0],
        """
        <abstract lang="swe" repeatId="0">
           Lorem ipsum dolor sit amet
        </abstract>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        abstracts[1],
        """
        <abstract lang="eng" repeatId="1">
            &lt;p&gt;Another summary, &lt;strong&gt;bold text&lt;/strong&gt;, &lt;em&gt;cursive text,&lt;/em&gt; &lt;sup&gt;to the power of text&lt;/sup&gt;, 
            &lt;sub&gt;subscript text&lt;/sub&gt;&lt;/p&gt;
            &lt;p&gt;A formula: 
            &lt;img src=&quot;http://www.diva-portal.org/cgi-bin/mimetex.cgi?
            %5Cbigcup_%7B2%7D%5E%7B3%5E%7Bb%7Dx%7D%5Cpm&quot; data-classname=&quot;equation&quot; data-title=&quot;&quot; /&gt;&lt;/p&gt;
        </abstract>
        """,
    )
