import unittest

from cora.client.AppTokenClient import AppTokenClient
from unittest.mock import MagicMock

class Test(unittest.TestCase):
    def setUp(self):
        self.mock_time = MagicMock()
        self.mock_threading = MagicMock()
        self.mock_requests = MagicMock()
        

        self.login_url = 'https://cora.epc.ub.uu.se/diva/login/rest/apptoken'
        self.login_id = 'divaAdmin@cora.epc.ub.uu.se'
        self.app_token = '49ce00fb-68b5-4089-a5f7-1c225d3cf156'
        
        self.dependencies = {"requests": self.mock_requests,
                             "time": self.mock_time,
                             "threading": self.mock_threading}
        self.spec = {"login_url": self.login_url,
                "login_id": self.login_id,
                "app_token": self.app_token}

    def tearDown(self):
        pass
    
    
    def test_init(self):
        self.client = AppTokenClient(self.dependencies, self.spec)
        
        self.assertNotEqual(self.client, None)
    
    def test_init_should_login(self):
        self.client = AppTokenClient(self.dependencies, self.spec)
        
        login_headers = {'Content-Type':'application/vnd.uub.login',
                         'Accept':'application/vnd.uub.authentication+json'}
        combined_login_id_app_token = self.login_id+'\n'+self.app_token
        self.mock_requests.post.assert_called_once_with(
            self.login_url, data=combined_login_id_app_token, headers=login_headers)
        

    
    def test_get_auth_token(self):
        self.set_up_response_answer(self.get_ok_login_answer()) 
        self.client = AppTokenClient(self.dependencies, self.spec)
        
        self.assertEqual(self.client.get_auth_token(), '5545e11c-7e90-4289-87d0-155bb2078f85')
    
    def test_get_auth_token2(self):
        login_answer = 'not ok login'
        mock_response = MagicMock()
        mock_response.json.return_value = login_answer
        self.mock_requests.post.return_value = mock_response 
        try:
            AppTokenClient(self.dependencies, self.spec)
            self.fail('shold have trown exception')
        except Exception as e:
            self.assertIsNotNone(e)
            self.assertEqual(str(e), "Token not found in response")
            
#        self.assertEqual(self.client.get_auth_token(), '5545e11c-7e90-4289-87d0-155bb2078f85')
    
    def set_up_response_answer(self, login_answer):
        mock_response = MagicMock()
        mock_response.json.return_value = login_answer
        self.mock_requests.post.return_value = mock_response
    
    def get_ok_login_answer(self):
        return {
            "authentication": {
                "data": {
                    "children": [
                        {
                            "name": "token",
                            "value": "5545e11c-7e90-4289-87d0-155bb2078f85"
                        },
                        {
                            "name": "validUntil",
                            "value": "1744703967172"
                        },
                        {
                            "name": "renewUntil",
                            "value": "1744789767172"
                        },
                        {
                            "name": "userId",
                            "value": "161616"
                        },
                        {
                            "name": "loginId",
                            "value": "divaAdmin@cora.epc.ub.uu.se"
                        },
                        {
                            "name": "firstName",
                            "value": "DiVA"
                        },
                        {
                            "name": "lastName",
                            "value": "Admin"
                        },
                        {
                            "repeatId": "1",
                            "children": [
                                {
                                    "name": "linkedRecordType",
                                    "value": "permissionUnit"
                                },
                                {
                                    "name": "linkedRecordId",
                                    "value": "test1"
                                }
                            ],
                            "name": "permissionUnit"
                        },
                        {
                            "repeatId": "2",
                            "children": [
                                {
                                    "name": "linkedRecordType",
                                    "value": "permissionUnit"
                                },
                                {
                                    "name": "linkedRecordId",
                                    "value": "test2"
                                }
                            ],
                            "name": "permissionUnit"
                        }
                    ],
                    "name": "authToken"
                },
                "actionLinks": {
                    "renew": {
                        "requestMethod": "POST",
                        "rel": "renew",
                        "url": "http://localhost:38182/login/rest/authToken/39d029d1-1262-42a7-82df-a0e64daeb3ec",
                        "accept": "application/vnd.uub.authentication+json"
                    },
                    "delete": {
                        "requestMethod": "DELETE",
                        "rel": "delete",
                        "url": "http://localhost:38182/login/rest/authToken/39d029d1-1262-42a7-82df-a0e64daeb3ec"
                    }
                }
            }
        }
if __name__ == "__main__":
    unittest.main()