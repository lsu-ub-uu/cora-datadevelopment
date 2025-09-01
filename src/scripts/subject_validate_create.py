import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.subject_transform import transform_subject

RECORD_TYPE = "diva-subject"

source_xml_file_path = "data/db_xml/subjects_varldskulturmuseerna.xml"
system = "preview"
login_id = "divaAdmin@cora.epc.ub.uu.se"
app_token = "49ce00fb-68b5-4089-a5f7-1c225d3cf156"
apply = False
workers = 16


def main():
    context = CoraContext(system, login_id, app_token)

    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context)

    cora_subjects = _transform_to_cora_subjects(source_records)

    #    for elem in cora_subjects:
    #        print(ET.tostring(elem, encoding='unicode'))

    validation_results = validate_record_list(cora_subjects, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_subjects, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context):
    source_data = common_data.read_source_xml(source_xml_file_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_subjects(source_records: list[ET.Element]):
    return run_with_threads(
        source_records,
        transform_subject,
        workers=workers,
        desc="Transforming new records",
    )


if __name__ == "__main__":
    main()
