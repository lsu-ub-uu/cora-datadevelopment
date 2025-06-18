import pytest
from fedora_to_cora.get_validation_type_by_publication_type_id import get_validation_type_by_publication_type_id

def test_known_publication_type_ids():
    assert get_validation_type_by_publication_type_id("50") == "publication_journal-article"
    assert get_validation_type_by_publication_type_id("67") == "diva_dissertation"
    assert get_validation_type_by_publication_type_id("71") == "artistic-work_original-creative-work"

def test_unknown_publication_type_id_raises_keyerror():
    with pytest.raises(KeyError):
        get_validation_type_by_publication_type_id("999")
    with pytest.raises(KeyError):
        get_validation_type_by_publication_type_id("")
    with pytest.raises(KeyError):
        get_validation_type_by_publication_type_id(None)
