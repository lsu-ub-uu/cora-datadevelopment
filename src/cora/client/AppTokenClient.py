class  AppTokenClient:
    def __init__(self, dependencies, spec):
        self.time = dependencies["time"]
        self.threading = dependencies["threading"]
        self.requests = dependencies["requests"]
        
        self.login_url = spec["login_url"]
        self.login_id = spec["login_id"]
        self.app_token = spec["app_token"]
        
        self.login_using_app_token()
    
    def login_using_app_token(self):
        try:
            login_headers = {'Content-Type':'application/vnd.uub.login',
                             'Accept':'application/vnd.uub.authentication+json'}
                
            combined_login_id_app_token = self.login_id+'\n'+self.app_token
            response = self.requests.post(self.login_url, data=combined_login_id_app_token, headers=login_headers)
            response_json = response.json()
    
            children = response_json["authentication"]["data"]["children"]
            for child in children:
                if child["name"] == "token":
                    self.auth_token = child["value"]
                    break
        except Exception as e:
            raise ValueError("Token not found in response")
#        else:
#            raise ValueError("Token not found in response")

        
    def get_auth_token(self):
        return self.auth_token
    
#    def schedule_token_refresh(self, valid_until_ms):
#        """
#        Schedule a call to self._get_new_token at the time specified by valid_until_ms (in milliseconds).
#        """
#    
#        # Convert to seconds
#        valid_until_sec = valid_until_ms / 1000
#    
#        # Optional buffer time (e.g. renew 5 seconds before actual expiry)
#        buffer = 5
#        delay = valid_until_sec - self.time.time() - buffer
#    
#        if delay > 0:
#            print(f"[Token Refresh] Will refresh in {delay:.2f} seconds.")
#            self.timer = self.threading.Timer(delay, self._get_new_token)
#            self.timer.start()
#        else:
#            print("[Token Refresh] Token already expired or very close to expiration. Refreshing now.")
#            self._get_new_token()
#
#    
#    
#    def get_authToken(self, system):
#        if AppTokenClient.authToken != None:
##            print("returning old token")
#            return AppTokenClient.authToken
#        try:
#            getAuthTokenUrl = AppTokenClient.token_url[system]+'login/rest/apptoken'
#            appToken = 'divaAdmin@cora.epc.ub.uu.se\n49ce00fb-68b5-4089-a5f7-1c225d3cf156'
#            json_headers = {'Content-Type':'application/vnd.uub.login', 'Accept':'application/vnd.uub.authentication+json'}
#            response = self.requests.post(getAuthTokenUrl, data=appToken, headers=json_headers)
#            response_json = response.json()
#            authToken = response_json['authentication']['data']['children'][0]['value']
#            AppTokenClient.authToken = authToken
#            return(authToken)
#        except self.requests.exceptions.JSONDecodeError:
#            print("Could not decode JSON response. Raw response:")
#            print(response.text)
##            raise
#            return AppTokenClient.get_authToken(system)
#        except Exception as e:
#            print("Error getting authToken:", e)
#            raise
#    token_url = {
#    'local': 'http://localhost:8182/',
#    'preview': 'https://cora.epc.ub.uu.se/diva/',
#    'mig': 'https://mig.diva-portal.org/',
#    'pre': 'https://pre.diva-portal.org/',
#}


    
   
    
