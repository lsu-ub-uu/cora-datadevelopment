import xml.etree.ElementTree as ET

from classic.db_client import execute_sql


def get_publishers(*, db_user: str, db_password: str) -> ET.Element:
    with open("src/classic/sql_scripts/publisher_select.sql", "r") as file:
        query = file.read()
    return execute_sql(query, db_user=db_user, db_password=db_password)
