import requests
import os
from dotenv import load_dotenv


def get_authority_person(
    authority_pid: str, *, authority_service_url: str | None = None
) -> dict:
    base_url = authority_service_url or os.getenv("AUTHORITY_SERVICE_URL")
    if not base_url:
        raise ValueError("AUTHORITY_SERVICE_URL environment variable is not set")
    response = requests.get(
        f"{base_url}/authority/rest/authority/person/{authority_pid}"
    )
    response.raise_for_status()

    return response.json()
