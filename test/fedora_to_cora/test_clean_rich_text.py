from fedora_to_cora.clean_rich_text import clean_rich_text
import pytest


def test_empty_input_returns_empty_string():
    assert clean_rich_text("") == ""


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


# Test cases for empty list items
def test_empty_list_items_ul():
    input = "&lt;ul&gt;&lt;li&gt;&lt;/li&gt;&lt;li&gt;Non-empty item&lt;/li&gt;&lt;li&gt;&lt;/li&gt;&lt;/ul&gt;"
    expected = "• Non-empty item"
    assert clean_rich_text(input) == expected


def test_empty_list_items_ol():
    input = "&lt;ol&gt;&lt;li&gt;&lt;/li&gt;&lt;li&gt;Content&lt;/li&gt;&lt;li&gt;&lt;/li&gt;&lt;/ol&gt;"
    expected = "1. Content"
    assert clean_rich_text(input) == expected


def test_mixed_empty_and_whitespace_list_items():
    input = "&lt;ul&gt;&lt;li&gt;&lt;/li&gt;&lt;li&gt;   &lt;/li&gt;&lt;li&gt;Real content&lt;/li&gt;&lt;/ul&gt;"
    expected = "• Real content"
    assert clean_rich_text(input) == expected


# Test cases for whitespace-only content
def test_whitespace_only_paragraph():
    input = "&lt;p&gt;   &lt;/p&gt;&lt;p&gt;Real content&lt;/p&gt;"
    expected = "Real content"
    assert clean_rich_text(input) == expected


def test_mixed_whitespace_characters():
    input = "&lt;p&gt;\t\n  \r&lt;/p&gt;&lt;p&gt;Content&lt;/p&gt;"
    expected = "Content"
    assert clean_rich_text(input) == expected


def test_paragraph_with_only_spaces():
    input = "&lt;p&gt;          &lt;/p&gt;&lt;p&gt;Next paragraph&lt;/p&gt;"
    expected = "Next paragraph"
    assert clean_rich_text(input) == expected


# Test cases for Unicode characters
def test_unicode_emoji():
    input = "&lt;p&gt;Hello world! 🌍 Welcome 👋&lt;/p&gt;"
    expected = "Hello world! 🌍 Welcome 👋"
    assert clean_rich_text(input) == expected


def test_unicode_special_characters():
    input = "&lt;p&gt;Café, naïve, résumé, piñata&lt;/p&gt;"
    expected = "Café, naïve, résumé, piñata"
    assert clean_rich_text(input) == expected


def test_unicode_mathematical_symbols():
    input = "&lt;p&gt;α + β = γ, ∑, ∞, ≠, ≤, ≥&lt;/p&gt;"
    expected = "α + β = γ, ∑, ∞, ≠, ≤, ≥"
    assert clean_rich_text(input) == expected


def test_unicode_chinese_characters():
    input = "&lt;p&gt;你好世界&lt;/p&gt;"
    expected = "你好世界"
    assert clean_rich_text(input) == expected


def test_unicode_arabic_characters():
    input = "&lt;p&gt;مرحبا بالعالم&lt;/p&gt;"
    expected = "مرحبا بالعالم"
    assert clean_rich_text(input) == expected


def test_unicode_in_lists():
    input = "&lt;ul&gt;&lt;li&gt;Item with emoji 🚀&lt;/li&gt;&lt;li&gt;Mathematical: α² + β²&lt;/li&gt;&lt;/ul&gt;"
    expected = "• Item with emoji 🚀\n• Mathematical: α² + β²"
    assert clean_rich_text(input) == expected


# Test cases for control characters
def test_control_characters_tab():
    input = "&lt;p&gt;Text\twith\ttabs&lt;/p&gt;"
    expected = "Text\twith\ttabs"
    assert clean_rich_text(input) == expected


def test_control_characters_newline():
    input = "&lt;p&gt;Line one\nLine two&lt;/p&gt;"
    expected = "Line one\nLine two"
    assert clean_rich_text(input) == expected


def test_control_characters_carriage_return():
    input = "&lt;p&gt;Text\rwith\rcarriage\rreturns&lt;/p&gt;"
    expected = "Text\rwith\rcarriage\rreturns"
    assert clean_rich_text(input) == expected


def test_mixed_control_characters():
    input = "&lt;p&gt;Mixed\t\n\r control chars&lt;/p&gt;"
    expected = "Mixed\t\n\r control chars"
    assert clean_rich_text(input) == expected


def test_control_characters_in_lists():
    input = "&lt;ul&gt;&lt;li&gt;Item\twith\ttab&lt;/li&gt;&lt;li&gt;Item\nwith\nnewline&lt;/li&gt;&lt;/ul&gt;"
    expected = "• Item\twith\ttab\n• Item\nwith\nnewline"
    assert clean_rich_text(input) == expected
