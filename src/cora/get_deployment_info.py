import requests
from cora.constants import BASE_URL


def get_deployment_info(system: str):
    url = BASE_URL[system].replace("/record/", "/")
    deployment_info = requests.get(
        url, headers={"Accept": "application/vnd.cora.deploymentInfo+json"}
    )
    deployment_info.raise_for_status()
    return deployment_info.json()
