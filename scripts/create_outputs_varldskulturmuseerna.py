from fedora_to_cora.output_create import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from common.common_data import read_source_xml

def main():
    source_record = read_source_xml("data/fedora_xml/1681782_varldskulturmuserna.xml")
    cora_output = transform_to_cora_output(source_record)
    print(pretty_print_xml(cora_output))

if __name__ == "__main__":
    main()
