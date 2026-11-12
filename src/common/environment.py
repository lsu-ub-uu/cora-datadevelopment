import os

from dotenv import load_dotenv


def load_environment() -> dict[str, str | int | None]:
    load_dotenv()

    return {
        "cora_url": os.getenv("CORA_URL"),
        "system": os.getenv("CORA_SYSTEM", "minikube"),
        "login_id": os.getenv("CORA_LOGIN_ID", "divaAdmin@cora.epc.ub.uu.se"),
        "app_token": os.getenv("CORA_APP_TOKEN"),
        "workers": int(os.getenv("CORA_WORKERS", "16")),
        "fedora_url": os.getenv("FEDORA_URL"),
        "fedora_authority_url": os.getenv("FEDORA_AUTHORITY_URL"),
        "solr_url": os.getenv("SOLR_URL"),
        "authority_service_url": os.getenv("AUTHORITY_SERVICE_URL"),
        "db_host": os.getenv("DB_HOST", "localhost"),
        "db_port": int(os.getenv("DB_PORT", "5432")),
        "db_name": os.getenv("DB_NAME", "auradb"),
        "db_user": os.getenv("DB_USER"),
        "db_password": os.getenv("DB_PASSWORD"),
    }
