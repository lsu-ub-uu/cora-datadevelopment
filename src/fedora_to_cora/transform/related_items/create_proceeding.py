import xml.etree.ElementTree as ET

from common.xml_utils import append_if_value, create_group, create_text
from fedora_to_cora.clean_rich_text import clean_rich_text
from fedora_to_cora.transform.create_origin_info import create_publisher
from fedora_to_cora.transform.identifiers.create_doi_se_libr import (
    create_identifier_doi,
)
from fedora_to_cora.transform.identifiers.create_isbn import create_identifier_type_isbn
from fedora_to_cora.transform.related_items.create_series import (
    create_related_item_type_series,
)
from cora.context import Context


def create_related_item_type_proceeding(
    source_record: ET.Element, context: Context
) -> ET.Element | None:
    return create_group(
        "relatedItem",
        type="proceeding",
        otherType="text",
        children=[
            _create_title_info(source_record),
            _create_statement_of_responsibility(source_record),
            _create_part(source_record),
            create_identifier_type_isbn(source_record),
            create_identifier_doi(source_record),
            create_related_item_type_series(source_record, context),
            create_publisher(source_record, context),
        ],
    )


def _create_title_info(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "titleInfo",
        children=[
            create_text(
                "title",
                clean_rich_text(source_record.findtext("./proceedingsTitle/title")),
            ),
            create_text(
                "subtitle",
                clean_rich_text(source_record.findtext("./proceedingsTitle/subTitle")),
            ),
        ],
    )


def _create_statement_of_responsibility(source_record: ET.Element) -> ET.Element | None:
    return create_text(
        "note",
        type="statementOfResponsibility",
        value=source_record.findtext("./proceedingsEditor"),
    )


def _create_part(source_record: ET.Element) -> ET.Element | None:
    return create_group(
        "part",
        children=[
            create_group(
                "detail",
                type="volume",
                children=[
                    create_text("number", value=source_record.findtext("./volume"))
                ],
            ),
            create_group(
                "detail",
                type="issue",
                children=[
                    create_text("number", value=source_record.findtext("./issueNumber"))
                ],
            ),
            create_group(
                "detail",
                type="artNo",
                children=[
                    create_text("number", value=source_record.findtext("./articleId"))
                ],
            ),
            create_group(
                "extent",
                children=[
                    create_text("start", value=source_record.findtext("./startPage")),
                    create_text("end", value=source_record.findtext("./endPage")),
                ],
            ),
        ],
    )
