from fedora_to_cora.output_create import transform_to_cora_output
from common.xml_utils import pretty_print_xml

if __name__ == "__main__":
    cora_output = transform_to_cora_output("data/fedora_xml/1681782_varldskulturmuserna.xml")
    print(pretty_print_xml(cora_output))
