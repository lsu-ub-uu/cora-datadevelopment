import xml.etree.ElementTree as ET
import requests
import urllib.parse
from cora.constants import BASE_URL


def get_organisation_id_by_old_id(
    old_id: str, *, base_url: str, auth_token: str
) -> str | None:
    """
    Fetch the Cora organisation ID using the old organisation ID.

    :param old_id: The old ID of the organisation to look up.
    :param base_url: The base URL of the Cora API.
    :param auth_token: The authentication token for the API.
    :return: The new organisation ID as a string, or None if not found.
    """

    request_url = f"{base_url}searchResult/diva-organisationSearch"

    headers = {"accept": "application/vnd.cora.recordList+xml"}
    search_data = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <search>
            <include>
                <includePart>
                    <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                </includePart>
            </include>
        </search>
    """
    search_data_clean = "".join(line.strip() for line in search_data.splitlines())
    encoded_search_data = urllib.parse.quote(search_data_clean)
    params = {"searchData": encoded_search_data}

    print(f"Request URL: {request_url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
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
    print(response_xml)


if __name__ == "__main__":
    # Example usage
    old_id = "885801"
    base_url = BASE_URL["pre"]
    auth_token = "your_auth_token_here"

    try:
        organisation_id = get_organisation_id_by_old_id(
            old_id, base_url=base_url, auth_token=auth_token
        )
        if organisation_id:
            print(f"Organisation ID for old ID {old_id}: {organisation_id}")
        else:
            print(f"No organisation found for old ID {old_id}.")
    except Exception as e:
        print(f"Error: {e}")
