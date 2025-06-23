from fedora_to_cora.output_create import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from common.common_data import read_source_xml
import os
import traceback

XML_DIR = "data/fedora_xml"


def transform_fedora_file(filename):
    print(f"--- Processing file: {filename} ---")
    filepath = os.path.join(XML_DIR, filename)
    source_record = read_source_xml(filepath)
    cora_output = transform_to_cora_output(source_record)
    print(f"--- Output for {filename} ---")
    print(pretty_print_xml(cora_output))


def main():  #
    for filename in os.listdir(XML_DIR):
        if filename.endswith(".xml"):
            try:
                transform_fedora_file(filename)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                traceback.print_exc()
                continue


if __name__ == "__main__":
    transform_fedora_file("1781879_varldskulturmuserna.xml")
    # main()
