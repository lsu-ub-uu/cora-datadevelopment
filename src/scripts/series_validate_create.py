import time
from cora.context import CoraContext, Context
from common import common_data
import xml.etree.ElementTree as ET
from common.threads import run_with_threads
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.series_transform import transform_series

RECORD_TYPE = "diva-series"

source_xml_file_path = "data/db_xml/series_smhi_from_db.xml"
system = "pre"
login_id = "divaAdmin@cora.epc.ub.uu.se"
app_token = "49ce00fb-68b5-4089-a5f7-1c225d3cf156"
apply = False
workers = 16


def main():
    context = CoraContext(system, login_id, app_token)

    context.log("Data processing started")
    starttime = time.time()

    source_records = _read_source_records(context)

    cora_series = _transform_to_cora_series(source_records)

    #    for elem in cora_series:
    #        print(ET.tostring(elem, encoding='unicode'))

    validation_results = validate_record_list(cora_series, RECORD_TYPE, context)

    if apply and all(valid for (valid, _) in validation_results):
        create_record_list(cora_series, RECORD_TYPE, context)

    context.log(f"Run time: {time.time() - starttime}")
    print(
        f"Processing completed in {time.time() - starttime}s. Output logged to {context.get_log_file_path()}"
    )


def _read_source_records(context: Context):
    source_data = common_data.read_source_xml(source_xml_file_path)
    source_records = [record for record in source_data.findall(".//DATA_RECORD")]
    context.log(f"Number of records read: {len(source_records)}")
    return source_records


def _transform_to_cora_series(source_records: list[ET.Element]):
    return run_with_threads(
        source_records,
        transform_series,
        workers=workers,
        desc="Transforming new records",
    )


if __name__ == "__main__":
    main()
