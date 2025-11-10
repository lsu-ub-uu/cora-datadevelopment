import requests


def download_attachment(pid: str, file_name: str) -> bytes:
    download_url = f"http://localhost:8088/fedora/get/{pid}/{file_name}"
    download_response = requests.get(download_url)
    download_response.raise_for_status()
    return download_response.content
