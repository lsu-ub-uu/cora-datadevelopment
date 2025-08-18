from fedora_to_cora.process_fedora_publication_files import (
    process_fedora_publication_files,
)

successful_transformations = []
failed_transformations = []

env = {
    "xml_dir": "data/fedora_xml/varldskulturmuseerna/20250625",
    "system": "pre",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
    "dry_run": True,  # Set to True to skip actual transformations
}


if __name__ == "__main__":
    process_fedora_publication_files(**env)
