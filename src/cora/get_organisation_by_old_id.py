import xml.etree.ElementTree as ET
import requests
from cora.constants import BASE_URL
from common.xml_utils import inline_xml_string

_cache: dict[str, str | None] = {}


def get_organisation_id_by_old_id(
    old_id: str, *, base_url: str, auth_token: str | None = None
) -> str | None:
    """
    Fetch the Cora organisation ID using the old organisation ID.

    :param old_id: The old ID of the organisation to look up.
    :param base_url: The base URL of the Cora API.
    :param auth_token: The authentication token for the API.
    :return: The new organisation ID as a string, or None if not found.
    """

    if old_id in _cache:
        return _cache[old_id]

    request_url = f"{base_url}searchResult/diva-organisationSearch"

    headers = {
        "accept": "application/vnd.cora.recordList+xml",
        "Authtoken": auth_token,
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
            f"Failed to fetch organisation ID: {response.status_code} {response.text}"
        )
    response_xml = ET.fromstring(response.text)
    record_ids = response_xml.findall(".//recordInfo/id")

    if len(record_ids) > 1:
        print(
            f"Warning: Multiple organisations found for old ID '{old_id}'. Using the first one."
        )
    elif len(record_ids) == 0:
        print(f"Warning: No organisations found for old ID '{old_id}'. Returning None.")

    record_id = record_ids[0] if record_ids else None

    result = record_id.text if record_id is not None else None
    _cache[old_id] = result
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
