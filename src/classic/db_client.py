from fabric import Connection
import psycopg2
import xml.etree.ElementTree as ET
from typing import Optional

SSH_HOST = "130.238.7.110"
SSH_PORT = 22
SSH_USER = "support"

LOCAL_PORT = 5432

REMOTE_HOST = "diva-storage1"
REMOTE_PORT = 5432

DB_NAME = "auradb"


def execute_sql(
    query: str,
    *,
    params: Optional[dict[str, str]] = None,
    db_user: str,
    db_password: str
) -> ET.Element:
    with Connection(host=SSH_HOST, port=SSH_PORT, user=SSH_USER).forward_local(
        local_port=LOCAL_PORT,
        remote_port=REMOTE_PORT,
        remote_host=REMOTE_HOST,
        local_host="localhost",
    ):
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


def _parse_response_to_xml(rows: list[tuple], colnames: list[str]) -> ET.Element:
    root = ET.Element("ROOT")
    for row in rows:
        data_record = ET.SubElement(root, "DATA_RECORD")
        for colname, colval in zip(colnames, row):
            elem = ET.SubElement(data_record, colname)
            if colval is not None:
                elem.text = str(colval)
    return root
