import unittest
from fedora_to_cora.get_validation_type_by_publication_type_id import get_validation_type_by_publication_type_id

class TestGetValidationTypeByPublicationTypeId(unittest.TestCase):
    def test_known_publication_type_ids(self):
        self.assertEqual(get_validation_type_by_publication_type_id("50"), "publication_journal-article")
        self.assertEqual(get_validation_type_by_publication_type_id("67"), "diva_dissertation")
        self.assertEqual(get_validation_type_by_publication_type_id("71"), "artistic-work_original-creative-work")

    def test_unknown_publication_type_id_raises_keyerror(self):
        with self.assertRaises(KeyError):
            get_validation_type_by_publication_type_id("999")
        with self.assertRaises(KeyError):
            get_validation_type_by_publication_type_id("")
        with self.assertRaises(KeyError):
            get_validation_type_by_publication_type_id(None)

if __name__ == "__main__":
    unittest.main()