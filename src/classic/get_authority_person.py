import requests
import os


def get_authority_person(
    authority_pid: str, *, authority_service_url: str | None = None
):
    base_url = authority_service_url or os.getenv("AUTHORITY_SERVICE_URL")
    if not base_url:
        raise ValueError("AUTHORITY_SERVICE_URL environment variable is not set")
    response = requests.get(
        f"{base_url}/authority/rest/authority/person/{authority_pid}"
    )
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
