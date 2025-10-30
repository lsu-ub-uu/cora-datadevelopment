import re
import html


def debug_clean_rich_text(input: str) -> str:
    print("=== Step 1: Input ===")
    print(repr(input[:100]))

    output = html.unescape(input)
    print("\n=== Step 2: After html.unescape ===")
    print(repr(output[:100]))

    # Test _format_blocks
    block_tags = ["p", "ol", "ul", "h1", "h2", "h3", "h4", "h5", "h6", "pre"]
    output = re.sub(r"<p>\s*</p>", "", output)
    for tag in block_tags:
        output = output.replace(f"</{tag}>", f"</{tag}>\n\n")
    print("\n=== Step 3: After _format_blocks ===")
    print(repr(output[:200]))

    return output


# Simple test
test_input = "&lt;p&gt;First paragraph.&lt;/p&gt;&lt;p&gt;Second paragraph.&lt;/p&gt;"
result = debug_clean_rich_text(test_input)
print("\n=== Final result ===")
print(result)
