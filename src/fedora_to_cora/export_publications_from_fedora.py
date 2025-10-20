from datetime import datetime
from common.run_rotating_logger import RunRotatingLogger
import xml.etree.ElementTree as ET
from classic.get_pids_for_domain import get_pids_for_domain
from classic.get_classic_publications import get_classic_publications
from common.xml_utils import save_to_file


def export_publications_from_fedora(domain: str, workers=16):
    time_started = _get_now()
    dirname = f"data/fedora_xml/{domain}/{time_started.isoformat()}"
    logger = RunRotatingLogger("data", f"logs/outputs_export.log").get()

    logger.info("==== Begin importing publications from Fedora ====")
    logger.info(f"==== domain={domain} ====")
    logger.info("==================================================")

    pids = get_pids_for_domain(domain)
    logger.info(f"Found {len(pids)} publications in domain {domain}")

    def handle_record_import_success(pid, record: ET.Element):
        try:
            save_to_file(record, f"{dirname}/{pid}.xml")
            logger.info(f"Successfully imported publication {pid}")
        except Exception as e:
            logger.error(f"Failed to save publication {pid} to file: {str(e)}")
            return

    get_classic_publications(
        pids,
        workers,
        on_success=handle_record_import_success,
        on_error=lambda error: logger.error(f"Failed to import publication {error}"),
    )

    logger.info(f"--- Successfully imported {len(pids)} publications to {dirname} ---")
    print(f"--- Successfully imported {len(pids)} publications to {dirname} ---")


def _get_now() -> datetime:
    return datetime.now()
