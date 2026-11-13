import xml.etree.ElementTree as ET
import logging
from cora_python_client import CoraClient
import requests
from common.xml_utils import inline_xml_string
from typing import Literal
from cora_python_client import CoraClient

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}

record_type_to_searchId = {
    "diva-funder": "diva-funderSearch",
    "diva-journal": "diva-journalSearch",
    "diva-organisation": "diva-organisationSearch",
    "diva-person": "diva-personSearch",
    "diva-publisher": "diva-publisherSearch",
    "diva-series": "diva-seriesSearch",
    "diva-subject": "diva-subjectSearch",
    "diva-course": "diva-courseSearch",
    "diva-project": "diva-projectSearch",
    "diva-programme": "diva-programmeSearch",
    "diva-output": "outputPublicSearch",
    "diva-oldRecord": "diva-oldRecordSearch",
}


def get_cora_id_by_old_id(
    old_id: str,
    *,
    record_type: Literal[
        "diva-organisation",
        "diva-person",
        "diva-publication",
        "diva-funder",
        "diva-journal",
        "diva-publisher",
        "diva-series",
        "diva-subject",
        "diva-course",
        "diva-project",
        "diva-programme",
        "diva-output",
        "diva-oldRecord",
    ],
    cora_client: CoraClient,
) -> str:
    """
    Fetch the Cora record ID using the old organisation ID.

    :param old_id: The old ID of the organisation to look up.
    :param record_type: The type of record to search for (e.g., "diva-organisation").
    :param base_url: The base URL of the Cora API.
    :param auth_token: The authentication token for the API.
    :return: The Cora record ID as a string, or None if not found.
    """

    cache_key = f"{record_type}:{old_id}"
    if cache_key in _cache:
        return _cache[cache_key]

    search_data = (
        _create_generic_id_search_data(old_id)
        if record_type in ["diva-output", "diva-person"]
        else _create_search_data(old_id)
    )

    search_result = cora_client.search_records(
        search_id=record_type_to_searchId[record_type], search_data=search_data
    )
    result_records = search_result.records

    if len(result_records) > 1:
        logger.warning(
            f"Warning: Multiple {record_type}s found for old ID '{old_id}'. Using the first one."
        )
    elif len(result_records) == 0:
        return f"{record_type} not found for old ID: {old_id}"

    result = result_records[0].id

    _cache[cache_key] = result
    return result


def _create_search_data(old_id: str) -> ET.Element:
    return ET.fromstring(f"""
        <search>
            <include>
                <includePart>
                    <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                </includePart>
            </include>
        </search>
    """)


def _create_generic_id_search_data(old_id: str) -> ET.Element:
    return ET.fromstring(f"""
        <search>
            <include>
                <includePart>
                    <genericIdSearchTerm>{old_id.replace(":", "?")}</genericIdSearchTerm>
                </includePart>
            </include>
        </search>
    """)
