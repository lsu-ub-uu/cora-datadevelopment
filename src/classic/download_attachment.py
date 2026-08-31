import requests


def download_attachment(pid: str, file_name: str, *, fedora_url: str):
    download_url = f"{fedora_url}/fedora/get/{pid}/{file_name}"
    download_response = requests.get(download_url, stream=True)
    download_response.raise_for_status()
    return download_response.content
