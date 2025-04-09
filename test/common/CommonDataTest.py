import unittest
from common.CommonData import CommonData


class Test(unittest.TestCase):


    def setUp(self):
        self.common_data = CommonData()


    def tearDown(self):
        pass


    def test_create_record_info(self):
        record_type = "someRecordType"
        
        record_info = self.common_data.create_record_info(record_type)
        
        self.assertIsNotNone(record_info)
        self.assertEqual(record_info.tag, "recordInfo")


if __name__ == "__main__":
    unittest.main()