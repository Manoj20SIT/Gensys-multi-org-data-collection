import urllib.parse


class OAuthHandler:
    def __init__(self, client_id: str, redirect_uri: str, scope: str, login_endpoint: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.login_endpoint = login_endpoint
        
        print("OAuthHandler initialized with:")
        print("CLIENT_ID:", self.client_id)
        print("REDIRECT_URI:", self.redirect_uri)
        print("SCOPE:", self.scope)
        print("LOGIN_ENDPOINT:", self.login_endpoint)

    
    def construct_auth_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "token",   # ✅ MUST BE CODE
            "scope": self.scope
        }

        return f"https://{self.login_endpoint}/oauth/authorize?{urllib.parse.urlencode(params)}"
