import xml.etree.ElementTree as ET
from cora.context import Context
import requests


def list_records(context: Context, record_type_id: str) -> list[ET.Element]:
    request_url = f"{context.get_base_url()}{record_type_id}"
    headers = {
        "Accept": "application/vnd.cora.recordList+xml",
        "authToken": context.get_auth_token(),
    }

    try:
        response = requests.get(request_url, headers=headers)

        response.raise_for_status()

        data_list = ET.fromstring(response.text)
        return data_list.findall("./data/record")
    except Exception as e:
        context.log(
            f"❌ Failed to list records of type {record_type_id}: {str(e)}",
            "error",
        )
        raise e


if __name__ == "__main__":
    from cora.context import CoraContext

    # Example usage

    context = CoraContext("preview", "divaAdmin@cora.epc.ub.uu.se", None)
    record_type_id = "metadata"

    try:
        records = list_records(context, record_type_id)
        print(f"Successfully listed {len(records)} records of type {record_type_id}.")
    except Exception as e:
        print(f"Error: {str(e)}")
