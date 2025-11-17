from fabric import Connection
import psycopg2
import xml.etree.ElementTree as ET
import time
from typing import Optional
from classic.config import SSH_HOST, SSH_PORT, SSH_USER
from common.ssh_tunnel import SSHTunnel


LOCAL_PORT = 5432
REMOTE_HOST = "diva-storage1"
REMOTE_PORT = 5432
DB_NAME = "auradb"


def execute_sql(
    query: str,
    *,
    params: Optional[dict[str, str]] = None,
    db_user: str,
    db_password: str,
) -> ET.Element:
    max_retries = 2
    retry_delay = 1  # seconds

    with SSHTunnel(SSH_HOST, SSH_PORT, SSH_USER, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT):
        last_exception = None

        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                with psycopg2.connect(
                    dbname=DB_NAME,
                    user=db_user,
                    password=db_password,
                    host="localhost",
                    port=LOCAL_PORT,
                ) as database_connection:
                    with database_connection.cursor() as cursor:
                        cursor.execute(query, params)
                        rows = cursor.fetchall()
                        assert cursor.description is not None
                        colnames = [name for name, *_ in cursor.description]
                        return _parse_response_to_xml(rows, colnames)
            except psycopg2.OperationalError as e:
                last_exception = e
                if "Connection refused" in str(e) and attempt < max_retries:
                    print(
                        f"Connection attempt {attempt + 1} failed, retrying in {retry_delay} second(s)..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    # Re-raise the exception if it's not a connection refused error
                    # or if we've exhausted all retries
                    raise

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected error: no connection attempts were made")


def _parse_response_to_xml(rows: list[tuple], colnames: list[str]) -> ET.Element:
    root = ET.Element("ROOT")
    for row in rows:
        data_record = ET.SubElement(root, "DATA_RECORD")
        for colname, colval in zip(colnames, row):
            elem = ET.SubElement(data_record, colname)
            if colval is not None:
                elem.text = str(colval)
    return root
