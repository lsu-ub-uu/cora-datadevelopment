from fedora_to_cora.create_output import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from common.common_data import read_source_xml
import os
import traceback
from cora import constants
from cora.cora_config import CoraConfig
import requests
import threading
import time
import sys


env = {
    "xml_dir": "data/fedora_xml",
    "system": "pre",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
}


def transform_fedora_file(filename, cora_config: CoraConfig):
    print(f"--- Processing file: {filename} ---")
    filepath = os.path.join(env["xml_dir"], filename)
    source_record = read_source_xml(filepath)
    cora_output = transform_to_cora_output(source_record, cora_config)
    print(f"--- Output for {filename} ---")
    print(pretty_print_xml(cora_output))
    output_dir = "output_xml"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.splitext(filename)[0] + "_cora.xml"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_print_xml(cora_output))


def main():  #
    cora_config = CoraConfig(
        system=env["system"],
        login_id=env["login_id"],
        app_token=env["app_token"],
    )

    for filename in os.listdir(env["xml_dir"]):
        if filename.endswith(".xml"):
            try:
                transform_fedora_file(filename, cora_config)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                traceback.print_exc()
                continue


if __name__ == "__main__":
    # transform_fedora_file(
    #     "1781879_varldskulturmuserna.xml",
    #     CoraConfig(env["system"], env["login_id"], env["app_token"]),
    # )
    main()
