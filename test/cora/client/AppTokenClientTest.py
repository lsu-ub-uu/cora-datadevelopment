import unittest

from cora.client.AppTokenClient import AppTokenClient
from unittest.mock import MagicMock

class Test(unittest.TestCase):
    def setUp(self):
        self.mock_requests = MagicMock()

        login_url = 'https://cora.epc.ub.uu.se/diva/'
        user_name = 'divaAdmin@cora.epc.ub.uu.se'
        app_token = '49ce00fb-68b5-4089-a5f7-1c225d3cf156'
        
        self.spec = {"login_url": login_url,
                "user_name": user_name,
                "app_token": app_token}
        self.dependencies = {"requests": self.mock_requests}
        self.client = AppTokenClient(self.dependencies, self.spec)

    def tearDown(self):
        pass
    
    
    def test_init(self):
        self.assertEqual(self.active_launcher.state, "ready")
        self.assertEqual(self.data, {"launcher_no": 10, "state": "ready"})
  
        
    

if __name__ == "__main__":
    unittest.main()