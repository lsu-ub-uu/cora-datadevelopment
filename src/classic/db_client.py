import psycopg2
import os
import xml.etree.ElementTree as ET
import time
from typing import Optional


def execute_sql(
    query: str,
    *,
    params: Optional[dict[str, str]] = None,
    db_host: str | None,
    db_port: int | None,
    db_name: str | None,
    db_user: str | None,
    db_password: str | None,
) -> ET.Element:
    db_host = db_host if db_host is not None else os.environ.get("DB_HOST", "localhost")
    db_port = db_port if db_port is not None else int(os.environ.get("DB_PORT", "5432"))
    db_name = db_name if db_name is not None else os.environ.get("DB_NAME", "auradb")
    db_user = db_user if db_user is not None else os.environ.get("DB_USER")
    db_password = (
        db_password if db_password is not None else os.environ.get("DB_PASSWORD")
    )
    if not db_user:
        raise ValueError("DB_USER is required for database access")
    if not db_password:
        raise ValueError("DB_PASSWORD is required for database access")

    max_retries = 2
    retry_delay = 1  # seconds

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            with psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
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
