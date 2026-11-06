"""
Analyze XML schema structure from authority person files.

Extracts a schema showing possible element paths, text examples, and
which elements repeat. Processes all files for a complete schema.
"""

from collections import defaultdict
from collections.abc import Iterable
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

from common.threads import run_with_threads

DEFAULT_XML_DIRECTORY = Path("data/fedora/authority_person_xml")
# Process all files

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main() -> None:
    try:
        if not DEFAULT_XML_DIRECTORY.is_dir():
            raise SystemExit("Authority person XML directory does not exist")

        # Get list of XML files
        logger.info(f"Scanning {DEFAULT_XML_DIRECTORY} for XML files")
        xml_files = sorted(DEFAULT_XML_DIRECTORY.glob("*.xml"))
        logger.info(f"Found {len(xml_files)} total XML files")

        if not xml_files:
            raise SystemExit("No XML files found")

        sample_files = xml_files
        logger.info(f"Processing all {len(sample_files)} files")

        schema = _build_schema(sample_files)

        if not schema:
            logger.warning("No schema data was extracted")
            return

        logger.info("Formatting schema report")
        report = _format_schema_report(schema)
        print(report)

        logger.info("Writing schema report to file")
        report_path = _write_schema_report(report)
        print(f"\nReport saved to {report_path}")
        logger.info(f"Schema analysis complete")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise


def _build_schema(xml_paths: Iterable[Path]) -> dict:
    """Build schema by analyzing all files in parallel."""
    xml_list = list(xml_paths)
    logger.info(f"Starting schema analysis on {len(xml_list)} files")

    results = run_with_threads(
        xml_list,
        _analyze_file_schema,
        desc="Analyzing XML schemas",
        workers=32,
    )

    # Separate schemas and presence tracking
    file_schemas = [schema for schema, _ in results]
    all_present_paths = [present_paths for _, present_paths in results]

    # Merge all file schemas into a single schema
    logger.info("Merging schemas from all files")
    merged_schema = {}
    for i, file_schema in enumerate(file_schemas):
        if (i + 1) % 100 == 0:
            logger.info(f"Merged {i + 1}/{len(xml_list)} files")
        _merge_schema(merged_schema, file_schema)

    # Track which paths are present in all files
    logger.info("Identifying required elements")
    required_paths = _identify_required_paths(all_present_paths)
    for path in required_paths:
        if path in merged_schema:
            merged_schema[path]["is_required"] = True

    logger.info(f"Schema merge complete. Found {len(merged_schema)} unique paths")
    logger.info(f"Found {len(required_paths)} required paths")
    return merged_schema


def _analyze_file_schema(xml_path: Path) -> dict:
    """Analyze a single XML file and extract its schema."""
    try:
        root = ET.parse(xml_path, parser=ET.XMLParser(encoding="utf-8")).getroot()
    except ET.ParseError as e:
        logger.warning(f"XML parse error in {xml_path.name}: {e}")
        return {}
    except OSError as e:
        logger.warning(f"IO error reading {xml_path.name}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error parsing {xml_path.name}: {e}")
        return {}

    schema = {}
    path_counts = {}  # Track how many times we've seen each path in this file
    try:
        _walk_element(root, schema, path="", path_counts=path_counts)
    except Exception as e:
        logger.error(f"Error walking tree in {xml_path.name}: {e}")
        return {}

    return schema, _get_present_paths(schema)


def _walk_element(
    element: ET.Element, schema: dict, path: str, path_counts: dict
) -> None:
    """Recursively walk an XML element and track schema information."""
    try:
        # Build current path
        if path:
            current_path = f"{path}.{element.tag}"
        else:
            current_path = element.tag

        # Get or create entry for this element
        if current_path not in schema:
            schema[current_path] = {
                "example": None,
                "is_repeating": False,
                "is_required": False,
                "children": set(),
            }

        # Capture text example if not already captured
        if schema[current_path]["example"] is None and element.text:
            text = element.text.strip()
            if text:
                # Limit example length to avoid memory issues
                schema[current_path]["example"] = text[:200]

        # Count sibling tags to detect repeats
        sibling_tag_counts = defaultdict(int)
        for child in element:
            sibling_tag_counts[child.tag] += 1

        # Mark tags that repeat among siblings
        repeating_tags = {tag for tag, count in sibling_tag_counts.items() if count > 1}

        # Recursively process each child
        for child in element:
            child_path = f"{current_path}.{child.tag}"
            # Ensure child_path exists in schema
            if child_path not in schema:
                schema[child_path] = {
                    "example": None,
                    "is_repeating": child.tag in repeating_tags,
                    "is_required": False,
                    "children": set(),
                }
            elif child.tag in repeating_tags:
                schema[child_path]["is_repeating"] = True
            _walk_element(child, schema, current_path, path_counts)
    except RecursionError as e:
        logger.error(f"Recursion limit hit at path {path}: {e}")
    except Exception as e:
        logger.error(f"Error walking element at path {path}: {e}")


def _merge_schema(target: dict, source: dict) -> None:
    """Merge source schema into target schema."""
    try:
        for path, info in source.items():
            if path not in target:
                target[path] = {
                    "example": info.get("example"),
                    "is_repeating": info.get("is_repeating", False),
                    "is_required": info.get("is_required", False),
                    "children": set(info.get("children", [])),
                }
            else:
                # Keep first example found
                if target[path]["example"] is None and info.get("example"):
                    target[path]["example"] = info["example"]
                # Mark as repeating if it was repeating in any file
                if info.get("is_repeating"):
                    target[path]["is_repeating"] = True
                # Merge children sets
                if info.get("children"):
                    target[path]["children"].update(info["children"])
    except Exception as e:
        logger.error(f"Error merging schema: {e}")


def _get_present_paths(schema: dict) -> set:
    """Get all paths that have non-empty examples in this schema."""
    return {path for path, info in schema.items() if info.get("example")}


def _identify_required_paths(all_present_paths: list[set]) -> set:
    """Identify paths that are present in all files (i.e., required)."""
    if not all_present_paths:
        return set()
    
    # Start with all paths from the first file
    required = set(all_present_paths[0])
    
    # Intersect with paths from each subsequent file
    for present_paths in all_present_paths[1:]:
        required &= present_paths
    
    return required


def _format_schema_report(schema: dict) -> str:
    """Format schema as a hierarchical tree with examples."""
    if not schema:
        return "No schema information found"

    # Build a tree structure from paths
    tree = _build_tree(schema)

    lines = []
    lines.append("XML Schema Structure")
    lines.append("=" * 60)

    # Traverse tree and output
    for element_name, element_info in tree.items():
        _format_tree_node(element_name, element_info, schema, lines, depth=0)

    return "\n".join(lines)


def _build_tree(schema: dict) -> dict:
    """Build a tree structure from flat paths."""
    tree = {}

    for path in schema.keys():
        parts = path.split(".")
        current_level = tree

        for i, part in enumerate(parts):
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    return tree


def _format_tree_node(
    element_name: str,
    element_info: dict,
    schema: dict,
    lines: list,
    depth: int,
    parent_path: str = "",
) -> None:
    """Format a tree node and its children recursively."""
    # Build the full path for this element
    if parent_path:
        full_path = f"{parent_path}.{element_name}"
    else:
        full_path = element_name

    indent = "    " * depth
    line = f"{indent}{element_name}"

    # Add example and markers if this element is in the schema
    if full_path in schema:
        info = schema[full_path]
        if info.get("example"):
            line += f" (\"{info['example']}\")"
        markers = []
        if info.get("is_required"):
            markers.append("[REQUIRED]")
        if info.get("is_repeating"):
            markers.append("[REPEATING]")
        if markers:
            line += " " + " ".join(markers)

    lines.append(line)

    # Recursively format children
    for child_name, child_info in sorted(element_info.items()):
        _format_tree_node(child_name, child_info, schema, lines, depth + 1, full_path)


def _write_schema_report(report: str, output_dir: Path = Path("reports")) -> Path:
    """Write schema report to file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "authority-person-xml-schema.txt"
    report_path.write_text(report, encoding="utf-8")

    return report_path


if __name__ == "__main__":
    main()
