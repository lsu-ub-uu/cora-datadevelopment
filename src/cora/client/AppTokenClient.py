class  AppTokenClient:
    authToken = None
    def __init__(self, dependencies, spec):
        self.requests = dependencies["requests"]
        
        self.login_url = spec["login_url"]
        self.user_name = spec["user_name"]
        self.app_token = spec["app_token"]
            
    
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
    
   
    
