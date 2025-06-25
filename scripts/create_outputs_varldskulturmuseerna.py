from fedora_to_cora.create_output import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from common.common_data import read_source_xml
import os
import traceback
from cora.context import CoraContext, Context
from cora.validate_record import validate_record


env = {
    "xml_dir": "data/fedora_xml/varldskulturmuseerna/20250625",
    "system": "pre",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
}


def transform_fedora_file(filename, context: Context):
    context.log(f"--- Processing file: {filename} ---")
    filepath = os.path.join(env["xml_dir"], filename)
    source_record = read_source_xml(filepath)
    cora_output = transform_to_cora_output(source_record, context)

    context.log(f"--- Output for {filename} ---")
    context.log(pretty_print_xml(cora_output))
    output_dir = "output_xml"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.splitext(filename)[0] + "_cora.xml"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_print_xml(cora_output))

    validate_record(
        cora_output,
        record_type="diva-output",
        auth_token=context.get_auth_token(),
        base_url=context.get_base_url(),
        logger=context.get_logger(),
    )


def main():  #
    context = CoraContext(
        system=env["system"],
        login_id=env["login_id"],
        app_token=env["app_token"],
    )

    context.log("==== Begin processing Fedora XML publications ====")
    context.log(f"==== {env} ====")
    context.log("==================================================")

    for filename in os.listdir(env["xml_dir"]):
        if filename.endswith(".xml"):
            try:
                transform_fedora_file(filename, context)
            except Exception as e:
                context.log(f"Error processing {filename}: {e}", "error")
                traceback.print_exc()
                continue


if __name__ == "__main__":
    main()
