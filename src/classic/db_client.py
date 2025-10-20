from fabric import Connection
import psycopg2
import xml.etree.ElementTree as ET
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
    db_password: str
) -> ET.Element:
    with SSHTunnel(SSH_HOST, SSH_PORT, SSH_USER, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT):
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
