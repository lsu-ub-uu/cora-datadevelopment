import psycopg2
import xml.etree.ElementTree as ET
import time
from typing import Optional


def execute_sql(
    query: str,
    *,
    params: Optional[dict[str, str]] = None,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
) -> ET.Element:
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
