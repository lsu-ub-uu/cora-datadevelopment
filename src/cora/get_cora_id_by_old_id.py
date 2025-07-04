import xml.etree.ElementTree as ET
import requests
from cora.constants import BASE_URL
from common.xml_utils import inline_xml_string
from cora.error import LinkedRecordNotFoundError
from logging import Logger
from typing import Literal
from cora.context import Context

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
    ],
    context: Context,
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

    request_url = (
        f"{context.get_base_url()}searchResult/{record_type_to_searchId[record_type]}"
    )

    headers = {
        "accept": "application/vnd.cora.recordList+xml",
        "Authtoken": context.get_auth_token(),
    }

    search_data = _create_search_data(old_id)
    params = {"searchData": inline_xml_string(search_data)}

    response = requests.get(
        request_url,
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch {record_type} ID: {response.status_code} {response.text}"
        )
    response_xml = ET.fromstring(response.text)
    record_ids = response_xml.findall(".//recordInfo/id")

    if len(record_ids) > 1:
        context.log(
            f"Warning: Multiple {record_type}s found for old ID '{old_id}'. Using the first one.",
            "warning",
        )
    elif len(record_ids) == 0:
        raise LinkedRecordNotFoundError(record_type, old_id=old_id)

    record_id = record_ids[0]

    result = record_id.text
    assert result is not None

    _cache[cache_key] = result
    return result


def _create_search_data(old_id: str) -> str:
    return f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <search>
            <include>
                <includePart>
                    <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                </includePart>
            </include>
        </search>
    """
