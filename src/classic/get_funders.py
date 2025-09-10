import xml.etree.ElementTree as ET

from classic.db_client import execute_sql


def get_funders():
    with open("data/db_xml/sql_scripts/funder_select.sql", "r") as file:
        query = file.read()
    return execute_sql(query)
