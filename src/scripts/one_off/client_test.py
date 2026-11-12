from cora_python_client import CoraValidationError
from cora_python_client.client import CoraClient
import logging
from common.arg_parser import create_argument_parser, common_arguments
import xml.etree.ElementTree as ET

from common.xml_utils import pretty_print_xml


def main():
    args = create_argument_parser(
        description="Test Cora client", arguments=common_arguments
    ).parse_args()

    print(args)
    client = CoraClient(args.cora_url)

    client.login_with_app_token(app_token=args.app_token, login_id=args.login_id)
    print("Logged in successfully")
    try:
        person_search_query = ET.fromstring("""
        <search>
            <include>
                <includePart>
                    <genericIdSearchTerm>**</genericIdSearchTerm>
                </includePart>
            </include>
        </search>
        """)
        current_persons = client.search_records(
            search_id="diva-personMinimalSearch", search_data=person_search_query
        )

        print("Current persons found:", len(current_persons.records))

        person_data = ET.fromstring("""<person>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-person</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                </recordInfo>
                <authority>
                    <name type="personal">
                        <namePart type="given">Leo</namePart>
                        <namePart type="chamily">Danielsson</namePart>
                    </name>
                    <fel>fel</fel>
                </authority>
            </person>""")
        try:
            client.validate_record(person_data, record_type="diva-person")
            print("person is valid")
        except CoraValidationError as e:
            print(f"{len(e.errors)} validation errors occurred:")
            for error in e.errors:
                print(error)
            return
        person = client.create_record(
            record_type="diva-person",
            data_group=person_data,
        )
        print("Created person record with ID: %s" % person.id)

        person.data_group.append(
            ET.fromstring('<email repeatId="1">leo@example.com</email>')
        )

        client.update_record(person)

        print(
            pretty_print_xml(
                client.get_record(
                    record_type="diva-person", record_id=person.id
                ).data_group
            )
        )
        client.delete_record(person)
        print("Deleted person record with ID: %s" % person.id)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
