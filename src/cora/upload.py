import requests
import xml.etree.ElementTree as ET
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common.xml_utils import pretty_print_xml
from cora.context import Context, CoraContext, MockContext
from cora.create import create_record


def upload_binary(binary_record: ET.Element, file_name: str, data, context: Context):
    upload_action_link = binary_record.find("./actionLinks/upload")
    assert (
        upload_action_link is not None
    ), "Upload action link not found in binary record"

    request_url = upload_action_link.findtext("./url")
    assert request_url is not None, "Upload URL not found in action link"

    multipart_data = MultipartEncoder(
        fields={
            "file": (
                file_name,
                data,
                "application/octet-stream",
            )
        }
    )

    response = requests.post(
        request_url,
        data=multipart_data,
        headers={
            "Authtoken": context.get_auth_token(),
            "Content-Type": multipart_data.content_type,
        },
    )

    if response.status_code == 200:
        context.log(f"Upload successful: {file_name} ")
    else:
        context.log(f"Upload failed: {response.text}")
        raise UploadError(
            f"Failed to upload binary file '{file_name}': {response.status_code} - {response.text}"
        )


class UploadError(Exception):
    """Custom exception for upload errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UploadError: {self.message}"


if __name__ == "__main__":
    context = CoraContext(
        system="minikube",
        login_id="divaAdmin@cora.epc.ub.uu.se",
        app_token="49ce00fb-68b5-4089-a5f7-1c225d3cf156",
        workers=16,
    )
    create_binary_result = create_record(
        ET.fromstring(
            """
                <binary type="generic"> 
                    <recordInfo>
                        <validationType>
                            <linkedRecordType>validationType</linkedRecordType>
                            <linkedRecordId>genericBinary</linkedRecordId>
                        </validationType>
                        <dataDivider>
                            <linkedRecordType>system</linkedRecordType>
                            <linkedRecordId>divaData</linkedRecordId>
                        </dataDivider>
                        <visibility>published</visibility>
                    </recordInfo>
                    <originalFileName>FULLTEXT01</originalFileName>
                </binary>   
        """
        ),
        record_type="binary",
        context=context,
    )

    print("created:", create_binary_result.record_id)

    download_url = f"http://localhost:8088/fedora/get/diva2:700257/FULLTEXT01"
    download_response = requests.get(download_url, stream=True)
    download_response.raise_for_status()

    print("downloaded from fedora")
    upload_binary(
        binary_record=create_binary_result.response_data,
        file_name="FULLTEXT01",
        data=download_response.raw,
        context=context,
    )
    print("uploaded to cora")
