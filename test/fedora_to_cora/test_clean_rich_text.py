from fedora_to_cora.clean_rich_text import clean_rich_text
import pytest


@pytest.mark.parametrize(
    "tag",
    [
        "em",
        "sub",
        "sup",
        "strong",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "pre",
    ],
)
def test_removes_text_formatting_tags(tag):
    input = f"&lt;{tag}&gt;Lorem ipsum.&lt;/{tag}&gt;"
    expected = "Lorem ipsum."
    assert clean_rich_text(input) == expected


def test_preserves_ul():
    input = "&lt;ul&gt;&lt;li&gt;Item one&lt;/li&gt;&lt;li&gt;Item two&lt;/li&gt;&lt;li&gt;Item three&lt;/li&gt;&lt;/ul&gt;"
    expected = "• Item one\n• Item two\n• Item three"
    assert clean_rich_text(input) == expected


def test_preserves_ol():
    input = "&lt;ol&gt;&lt;li&gt;Item one&lt;/li&gt;&lt;li&gt;Item two&lt;/li&gt;&lt;li&gt;Item three&lt;/li&gt;&lt;/ol&gt;"
    expected = "1. Item one\n2. Item two\n3. Item three"
    assert clean_rich_text(input) == expected


def test_adds_spaces_after_lists_ol():
    input = "&lt;ol&gt;&lt;li&gt;Item one&lt;/li&gt;&lt;/ol&gt;&lt;ul&gt;&lt;li&gt;Item one&lt;/li&gt;&lt;/ul&gt;"
    expected = "1. Item one\n\n• Item one"
    assert clean_rich_text(input) == expected


def xcreates_math_from_img_with_latex():
    pass


def test_clean_string_with_nested_tags():
    input = "&lt;p&gt;För ytterligare &lt;em&gt;information&lt;/em&gt; kontakta FMV:s bibliotek&lt;/p&gt;"
    expected = "För ytterligare information kontakta FMV:s bibliotek"
    assert clean_rich_text(input) == expected


def test_preserves_paragraphs():
    input = "&lt;p&gt;This is the first paragraph&lt;/p&gt;&lt;p&gt;This is the second paragraph&lt;/p&gt;&lt;p&gt;This is the third paragraph&lt;/p&gt;"
    expected = """This is the first paragraph\n\nThis is the second paragraph\n\nThis is the third paragraph"""
    assert clean_rich_text(input) == expected


def test_paragraph_with_other_tag():
    input = "&lt;p&gt;Innehåll&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Utgångspunkter och mål under Finlands ordförandeskap år 2007&lt;/li&gt;&lt;li&gt;Integration och mångfald i Norden&lt;/li&gt;&lt;li&gt;Medborgarinflytande&lt;/li&gt;&lt;li&gt;Om Finlands mål under ordförandeskapet&lt;/li&gt;&lt;li&gt;Forskning, innovation och välfärd&lt;/li&gt;&lt;li&gt;EU och den nordliga dimensionen&lt;/li&gt;&lt;li&gt;Närhet och rörlighet&lt;/li&gt;&lt;li&gt;Branding och effektivisering av det nordiska samarbetet&lt;/li&gt;&lt;/ul&gt;"
    expected = """Innehåll

• Utgångspunkter och mål under Finlands ordförandeskap år 2007
• Integration och mångfald i Norden
• Medborgarinflytande
• Om Finlands mål under ordförandeskapet
• Forskning, innovation och välfärd
• EU och den nordliga dimensionen
• Närhet och rörlighet
• Branding och effektivisering av det nordiska samarbetet"""
    assert clean_rich_text(input) == expected


def test_handles_empty_paragraph():
    input = "&lt;p&gt;First&lt;/p&gt;&lt;p&gt;&lt;/p&gt;&lt;p&gt;&lt;strong&gt;Second&lt;/strong&gt;&lt;/p&gt;"
    expected = "First\n\nSecond"
    assert clean_rich_text(input) == expected


@pytest.mark.parametrize(
    "escaped_char, expected_char",
    [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&apos;", "'"),
        ("&#39;", "'"),
        ("&#34;", '"'),
        ("&#60;", "<"),
        ("&#62;", ">"),
        ("&#38;", "&"),
    ],
)
def test_unescapes_html_entities(escaped_char, expected_char):
    input = f"&lt;p&gt;Text with {escaped_char} character&lt;/p&gt;"
    expected = f"Text with {expected_char} character"
    assert clean_rich_text(input) == expected


def test_unescapes_multiple_html_entities():
    input = (
        "&lt;p&gt;Johnson &amp;amp; Johnson &quot;quote&quot; &lt; 5 &gt; 3&lt;/p&gt;"
    )
    expected = 'Johnson & Johnson "quote" < 5 > 3'
    assert clean_rich_text(input) == expected


def test_unescapes_html_entities_in_lists():
    input = "&lt;ul&gt;&lt;li&gt;R&amp;amp;D department&lt;/li&gt;&lt;li&gt;Sales &amp;amp; Marketing&lt;/li&gt;&lt;/ul&gt;"
    expected = "• R&D department\n• Sales & Marketing"
    assert clean_rich_text(input) == expected
