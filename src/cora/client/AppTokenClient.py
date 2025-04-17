from cora.client.LoginError import LoginError
class  AppTokenClient:
    LOGIN_HEADERS = {'Content-Type':'application/vnd.uub.login',
                      'Accept':'application/vnd.uub.authentication+json'}
    
    def __init__(self, dependencies):
        self.time = dependencies["time"]
        self.threading = dependencies["threading"]
        self.requests = dependencies["requests"]

    def login(self, login_spec):
        try:
            self.try_to_login(login_spec)
        except Exception as e:
            raise LoginError("Login failed", e) from e

    def try_to_login(self, login_spec):
        response = self.login_using_spec(login_spec)
        self._handle_login_response(response)

    def _handle_login_response(self, response):
        if 201 != response.status_code:
            raise LoginError(f"Login failed: Expected 201, got {response.status_code}")
        self.schedule_token_refresh(response)
        self.auth_token = self.get_child_from_response_data(response, "token")
        
    def login_using_spec(self, login_spec):
        combined = self.create_combined_login_id_app_token(login_spec)
        login_url = login_spec["login_url"]
        return self.requests.post(login_url, data=combined, headers=AppTokenClient.LOGIN_HEADERS)

    def create_combined_login_id_app_token(self, login_spec):
        app_token = login_spec["app_token"]
        login_id = login_spec["login_id"]
        return login_id + '\n' + app_token
    
    def schedule_token_refresh(self, response):
        valid_until = int(self.get_child_from_response_data(response, "validUntil"))
        delay = self.calculate_delay_based_on_valid_until(valid_until)
        renew = self.get_renew_from_response(response)
        self.timer = self.threading.Timer(delay, self._get_new_token, args =[renew])
        
    def calculate_delay_based_on_valid_until(self, valid_until):
        valid_until_sec = valid_until / 1000
        buffer = 10
        delay = valid_until_sec - self.time.time() - buffer
        return delay

    def _get_new_token(self, renew):
        url = renew["url"]
        accept = renew["accept"]
        headers = {"Accept": accept,
                   "authToken": self.get_auth_token()}
        response = self.requests.post(url, headers=headers)
        self._handle_login_response(response)
    
    def get_renew_from_response(self, response):
        response_json = response.json()
        return response_json["authentication"]["actionLinks"]["renew"]
    
    def get_child_from_response_data(self, response, name_in_data):
        response_json = response.json()
        children = response_json["authentication"]["data"]["children"]
        for child in children:
            if child["name"] == name_in_data:
                return child["value"]
        
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


    
   
    
