import xml.etree.ElementTree as ET

from classic.db_client import execute_sql


def get_subjects(
    *, domain: str, db_host: str, db_port: int, db_name: str, db_user: str, db_password: str
) -> ET.Element:
    with open("src/classic/sql_scripts/subject_select.sql", "r") as file:
        query = file.read()
    return execute_sql(
        query,
        params={"domain": domain, "subject_type_id": "53"},
        db_host=db_host, db_port=db_port, db_name=db_name,
        db_user=db_user, db_password=db_password,
    )
