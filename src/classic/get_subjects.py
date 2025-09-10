import xml.etree.ElementTree as ET

from classic.db_client import execute_sql


def get_subjects(*, db_user: str, db_password: str) -> ET.Element:
    with open("data/db_xml/sql_scripts/subject_select.sql", "r") as file:
        query = file.read()
    return execute_sql(query, db_user=db_user, db_password=db_password)
