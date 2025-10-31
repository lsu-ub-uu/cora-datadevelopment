#!/usr/bin/env python3
"""
Temporary script to find XPath patterns that contain escaped HTML entities
in XML files from the fedora_xml/nordiskamuseet directory.
"""

import os
import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from pathlib import Path


def contains_html_entities(text):
    """Check if text contains escaped HTML entities like &gt;, &lt;, etc."""
    if not text:
        return False

    # Common HTML entities (escaped)
    html_entities = ["&gt;", "&lt;", "&amp;", "&quot;", "&#x", "&#"]

    return any(entity in text for entity in html_entities)


def extract_html_tags(text):
    """Extract HTML tags from text containing escaped HTML entities."""
    if not text or not contains_html_entities(text):
        return set(), []

    html_tags = set()
    img_examples = []

    # Find HTML tag patterns in escaped content
    # Look for patterns like &lt;tagname&gt; and &lt;/tagname&gt;
    tag_pattern = r"&lt;/?([a-zA-Z][a-zA-Z0-9]*)[^&]*?&gt;"
    matches = re.findall(tag_pattern, text)

    for match in matches:
        html_tags.add(match.lower())

    # Specifically look for img tags with their full content
    img_pattern = r"&lt;img[^&]*?&gt;"
    img_matches = re.findall(img_pattern, text, re.IGNORECASE)
    img_examples.extend(img_matches)

    return html_tags, img_examples


def get_element_xpath(element, root):
    """Generate XPath for an element relative to root."""
    if element == root:
        return f"/{element.tag}"

    path_parts = []
    current = element

    while current != root and current is not None:
        tag = current.tag

        # Find siblings with same tag to determine index
        parent = current.getparent() if hasattr(current, "getparent") else None
        if parent is not None:
            siblings = [child for child in parent if child.tag == tag]
            if len(siblings) > 1:
                index = siblings.index(current) + 1
                tag = f"{tag}[{index}]"

        path_parts.append(tag)
        current = parent

    path_parts.reverse()
    return "/" + "/".join(path_parts)


def find_simple_xpath_pattern(element_path):
    """Convert specific xpath to a general pattern."""
    # Remove array indices to create general patterns
    pattern = re.sub(r"\[\d+\]", "", element_path)
    return pattern


def analyze_xml_file(file_path):
    """Analyze a single XML file and return XPaths containing HTML entities."""
    html_xpaths = set()

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Walk through all elements
        for elem in root.iter():
            # Check element text
            if elem.text and contains_html_entities(elem.text):
                xpath_pattern = find_simple_xpath_pattern(get_element_path(elem, root))
                html_xpaths.add(xpath_pattern)

            # Check element tail text
            if elem.tail and contains_html_entities(elem.tail):
                xpath_pattern = find_simple_xpath_pattern(get_element_path(elem, root))
                html_xpaths.add(xpath_pattern)

            # Check attributes
            for attr_name, attr_value in elem.attrib.items():
                if contains_html_entities(attr_value):
                    xpath_pattern = (
                        find_simple_xpath_pattern(get_element_path(elem, root))
                        + f"/@{attr_name}"
                    )
                    html_xpaths.add(xpath_pattern)

    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return html_xpaths


def get_element_path(element, root):
    """Get the path from root to element."""
    if element == root:
        return f"/{element.tag}"

    path = []
    current = element

    # Build path from element to root
    while current is not None and current != root:
        path.append(current.tag)
        # Find parent manually since we're using ElementTree
        parent = None
        for candidate in root.iter():
            if current in candidate:
                parent = candidate
                break
        current = parent

    if path:
        path.reverse()
        return "/" + "/".join([root.tag] + path)
    else:
        return f"/{root.tag}"


def analyze_xml_file_simple(file_path):
    """Analyze XML file and return full XPaths for elements containing HTML entities."""
    html_xpaths = set()
    html_tags_found = set()
    img_examples = []

    try:
        # Read the raw content to find HTML entities
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Find all XML elements that contain HTML entities using regex
        # This pattern looks for opening tag, content with HTML entities, closing tag
        element_pattern = (
            r"<([^/][^>]*?)>([^<]*(?:&gt;|&lt;|&amp;|&quot;|&#)[^<]*)</([^>]*?)>"
        )
        matches = re.finditer(element_pattern, raw_content, re.MULTILINE | re.DOTALL)

        found_elements = set()

        for match in matches:
            opening_tag = match.group(1).strip()
            content = match.group(2)
            closing_tag = match.group(3).strip()

            # Extract tag name from opening tag (remove attributes)
            tag_name = opening_tag.split()[0] if " " in opening_tag else opening_tag

            # Verify opening and closing tags match
            if tag_name == closing_tag and contains_html_entities(content):
                found_elements.add(tag_name)
                # Extract HTML tags from this content
                tags, img_examples_from_content = extract_html_tags(content)
                html_tags_found.update(tags)
                img_examples.extend(img_examples_from_content)

        # Now parse the XML properly to build full XPaths for the found elements
        tree = ET.parse(file_path)
        root = tree.getroot()

        def traverse_element(elem, path=""):
            # Build the current full path
            if path == "":
                current_path = f"/{elem.tag}"
            else:
                current_path = f"{path}/{elem.tag}"

            # If this element type was found to contain HTML entities, add its path
            if elem.tag in found_elements:
                html_xpaths.add(current_path)

            # Recursively check children
            for child in elem:
                traverse_element(child, current_path)

        traverse_element(root)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return html_xpaths, html_tags_found, img_examples


def main():
    """Main function to analyze all XML files in the directory."""
    # Test with both directories
    test_dirs = [
        # "/home/leo/Repos/cora-datadevelopment/data/fedora_xml/nordiskamuseet/2025-10-20T10:19:00.783965",
        "/home/leo/Repos/cora-datadevelopment/data/fedora_xml/kth/2025-10-31T09:00:44.155153",
        # "/home/leo/Repos/cora-datadevelopment/data/fedora_xml/uu/2025-10-31T09:06:10.939513",
    ]

    for xml_dir in test_dirs:
        if not os.path.exists(xml_dir):
            print(f"Directory not found: {xml_dir}")
            continue

        print(f"\nAnalyzing XML files in: {xml_dir}")
        print("Looking for XPath patterns that contain escaped HTML entities...\n")

        all_html_xpaths = set()
        all_html_tags = set()
        all_img_examples = []
        files_with_img = []
        processed_files = 0
        files_with_html = 0

        # Process all XML files
        for filename in os.listdir(xml_dir):
            if filename.endswith(".xml"):
                file_path = os.path.join(xml_dir, filename)
                html_xpaths, html_tags, img_examples = analyze_xml_file_simple(
                    file_path
                )
                if html_xpaths:
                    files_with_html += 1
                if img_examples:
                    files_with_img.append(filename)
                    all_img_examples.extend(
                        [(filename, example) for example in img_examples]
                    )
                all_html_xpaths.update(html_xpaths)
                all_html_tags.update(html_tags)
                processed_files += 1

                if processed_files % 100 == 0:
                    print(f"Processed {processed_files} files...")

        print(f"\nResults for {os.path.basename(xml_dir)}:")
        print(f"Processed {processed_files} XML files.")
        print(f"Found HTML entities in {files_with_html} files.")
        print(
            f"Found {len(all_html_xpaths)} unique XPath patterns containing HTML entities."
        )
        print(f"Found {len(all_html_tags)} unique HTML tags in the content.")
        print(f"Found img tags in {len(files_with_img)} files.\n")

        # Sort and display results
        sorted_xpaths = sorted(all_html_xpaths)
        sorted_html_tags = sorted(all_html_tags)

        print("Rich text fields:")
        for xpath in sorted_xpaths:
            print(f" {xpath}")

        print(f"\nHTML tags found in the content:")
        for tag in sorted_html_tags:
            print(f" <{tag}>")

        if not sorted_html_tags:
            print(" (No HTML tags found)")

        # Show img tag examples and files
        if all_img_examples:
            print(f"\nIMG tag examples and files:")
            print(
                f"Found {len(all_img_examples)} img tag instances in {len(files_with_img)} files"
            )

            # Show up to 10 examples
            for i, (filename, img_example) in enumerate(all_img_examples[:10]):
                # Unescape the HTML for display
                unescaped_example = (
                    img_example.replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&amp;", "&")
                    .replace("&quot;", '"')
                )
                print(f"  File: {filename}")
                print(f"    {unescaped_example}")
                print()

            if len(all_img_examples) > 10:
                print(f"  ... and {len(all_img_examples) - 10} more img tag instances")

            print(f"\nFiles containing img tags:")
            for filename in sorted(set(files_with_img)):
                print(f"  {filename}")
        else:
            print(f"\nNo img tags found in this dataset.")

        print(f"\nTotal unique HTML tags: {len(sorted_html_tags)}")
        print(f"Total unique XPath patterns: {len(sorted_xpaths)}")
        print("-" * 80)


if __name__ == "__main__":
    main()
