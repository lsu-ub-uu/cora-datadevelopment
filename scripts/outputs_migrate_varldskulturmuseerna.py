from fedora_to_cora.output_transform import transform_to_cora_output
from common.xml_utils import pretty_print_xml
from common.common_data import read_source_xml
import os
import traceback
from cora.context import CoraContext, Context
from cora.validate import validate_record
from cora.create import create_record

successful_transformations = []
failed_transformations = []

env = {
    "xml_dir": "data/fedora_xml/varldskulturmuseerna/20250625",
    "system": "pre",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
    "dry_run": True,  # Set to True to skip actual transformations
}


def main():
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

    context.log("==== Processing complete ====")

    context.log(f"{len(successful_transformations)} Successful transformations:")
    for filename in successful_transformations:
        context.log(f"✅ {filename}")

    context.log(f"{len(failed_transformations)} Failed transformations:")
    for filename in failed_transformations:
        context.log(f"❌ {filename}")

    print(
        f"{len(successful_transformations)} succeeded, {len(failed_transformations)} failed."
    )
    print(f"Output logged to {context.get_logger().handlers[0].baseFilename}")  # type: ignore[attr-defined]


def transform_fedora_file(filename, context: Context):
    context.log(f"--- Processing file: {filename} ---")

    source_record = read_source_record_from_file(filename)

    cora_output = transform_to_cora_output(source_record, context)

    context.log(f"--- Output for {filename} ---")
    context.log(pretty_print_xml(cora_output))

    write_output_to_file(cora_output, filename)

    if env["dry_run"]:
        valid, errors = validate_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )
    else:
        valid, errors = create_record(
            cora_output,
            record_type="diva-output",
            context=context,
        )

    if valid:
        successful_transformations.append(filename)
    else:
        failed_transformations.append(
            f"{filename} - Errors: [{', '.join(errors) if errors else ''}]"
        )


def read_source_record_from_file(filename):
    filepath = os.path.join(env["xml_dir"], filename)
    source_record = read_source_xml(filepath)
    return source_record


def write_output_to_file(output, filename):
    output_dir = "output_xml"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.splitext(filename)[0] + "_cora.xml"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_print_xml(output))


if __name__ == "__main__":
    main()
