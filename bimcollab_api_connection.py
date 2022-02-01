from requests.auth import HTTPBasicAuth
import requests
import webbrowser
import urllib.parse
import winreg
import json
import base64
import hashlib
import re
import os


def save_refresh_token(token_value):
    # helper function to store the refresh token in the registry
    try:
        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\")
        newKey = winreg.CreateKey(key, "Genoa\\PDF_00")
        winreg.SetValueEx(newKey, "RefreshToken", 0, winreg.REG_SZ, token_value)
        if newKey:
            winreg.CloseKey(newKey)
    except Exception as e:
        print("Trouble saving RefreshToken to WinReg", e)


def read_refresh_token():
    # helper function to fetch he refresh token from the registry
    try:
        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Genoa\\PDF_00")
        value = winreg.QueryValueEx(key, "RefreshToken")
        if key:
            winreg.CloseKey(key)
        return value[0]
    except Exception as e:
        pass
        # print("Trouble fetching RefreshToken from WinReg", e)
    return None


def _b64_decode(data):
    import base64
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8')


def jwt_payload_decode(jwt):
    _, payload, _ = jwt.split('.')
    return json.loads(_b64_decode(payload))


def make_PKCE():
    """
    PKCE Tricks were plucked from this guide.
    https://www.stefaanlippens.net/oauth-code-flow-pkce.html
    """
    # this function creates PKCE verification and challenge codes
    verif = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    verif = re.sub('[^a-zA-Z0-9]+', '', verif)
    chall = hashlib.sha256(verif.encode('utf-8')).digest()
    chall = base64.urlsafe_b64encode(chall).decode('utf-8')
    chall = chall.replace('=', '')
    return verif, chall


class BearerAuth(requests.auth.AuthBase):
    # replace the function __call__ in AuthBase
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class ConnectionClient:
    def __init__(self):
        self._BIMCollab_space = "https://playground.bimcollab.com"
        self._authorize_url = self._BIMCollab_space + "/identity/connect/authorize"
        self._token_url = self._BIMCollab_space + "/identity/connect/token"
        self._state = "fooobarbaz"  # state = str(uuid.uuid4())
        self._client_id = "PlayGround_Client"
        self._client_secret = "k!xWcjad!u@L%ZWHc%%yKtMTqR%o1be@qWfWYaDL"
        self._HTTP_auth = HTTPBasicAuth(self._client_id, self._client_secret)
        self._callback_uri = "http://localhost:5000/Callback"
        self._scope = "openid offline_access bcf"
        self._RefreshTokenRegKey = "HKEY_CURRENT_USER\\SOFTWARE\\GENOA\\Connection API Sample"
        self._RefreshTokenRegVal = "RefreshToken"
        self._api_version = self._get_version()
        self._PKCE_verifier, self._PKCE_challenge = make_PKCE()
        self._access_token = None
        self._id_token = None
        self._auth_header = None
        self._login_name = None
        self._login_id = None


    def get_space(self):
        return self._BIMCollab_space

    def get_api_version(self):
        return self._api_version

    def get_auth_header(self):
        return self._auth_header

    def log_in(self):
        new_refresh_token = None
        # check to see if there is a valid refresh token from the registry.
        r_token = read_refresh_token()
        if r_token is not None:  # try to use it
            print("Refresh Token Located In WinReg")
            self._access_token, new_refresh_token, self._id_token = self._get_refresh_token(r_token)

        if new_refresh_token is None:
            print("No Refresh Token Located, or Refresh Token Invalid")
            # no refresh token, so get authorization code first, then tokens
            auth_code = self._get_authorization()
            self._access_token, new_refresh_token, self._id_token = self._get_token(auth_code)

        if new_refresh_token is None:
            # still not logged in so bail.
            return 0

        save_refresh_token(new_refresh_token)  # save the new refresh token to registry
        # rt = jwt_payload_decode(self._refresh_token)
        # print(rt)

        # create the header from the access token that we will need to hit the API
        self._auth_header = BearerAuth(self._access_token)
        # Get Current User to prove authentication
        user_url = "{}/bcf/{}/current-user".format(self._BIMCollab_space, self._api_version)
        r = requests.get(user_url, auth=self._auth_header)
        self._login_name = r.json()["name"]
        self._login_id = r.json()["id"]
        print("Successful Login!...")
        print("Name:", self._login_name)
        print("ID:", self._login_id)

        return 1  # success

    def _get_version(self):
        # there are 2 versions... 2.1 and an extended bc_2.1
        # we are expecting to use bc_2.1
        st = "{}/bcf/versions".format(self._BIMCollab_space)
        r = requests.get(st).json()
        return r["versions"][1]["version_id"]

    def _get_token(self, auth_code):
        # retrieve the access_token using the authorization code
        r = requests.post(
            url=self._token_url,
            auth=self._HTTP_auth,
            verify=False,
            data={
                "grant_type": "authorization_code",
                "client_id": self._client_id,
                "redirect_uri": self._callback_uri,
                "code": auth_code,
                "code_verifier": self._PKCE_verifier,
            },
            allow_redirects=False
        )
        if r.status_code != 200:
            print("Can't Get Tokens from Authorization Code... Quiting..")
            exit()
        r_json = r.json()
        access_token = r_json['access_token']
        refresh_token = r_json['refresh_token']
        id_token = r_json['id_token']
        return access_token, refresh_token, id_token

    def _get_refresh_token(self, saved_refresh_token):
        # Retrieve the authentication token using the saved refresh token
        r = requests.post(
            url=self._token_url,
            auth=self._HTTP_auth,
            verify=False,
            data={
                "grant_type": "refresh_token",
                "refresh_token": saved_refresh_token,
            },
            allow_redirects=False
        )
        # print(r.json())
        if r.status_code != 200:
            print("Can't Get Tokens from Refresh Token... Quiting..")
            print("status code:", r.status_code)
            return None, None, None

        r_json = r.json()
        access_token = r_json['access_token']
        refresh_token = r_json['refresh_token']
        id_token = r_json['id_token']
        return access_token, refresh_token, id_token

    def _get_authorization(self):
        r = requests.get(
            self._authorize_url,
            params={
                "response_type": "code",
                "client_id": self._client_id,
                "scope": self._scope,
                "redirect_uri": self._callback_uri,
                "state": self._state,
                "code_challenge": self._PKCE_challenge,
                "code_challenge_method": "S256"
            },
            allow_redirects=False
        )
        # open web browser pointed at this URL
        target = r.headers["Location"]
        webbrowser.open(target)
        full_response = input("Paste Entire Returned URL Here:")
        parts = urllib.parse.urlparse(full_response)
        query_dict = urllib.parse.parse_qs(parts.query)
        auth_code = query_dict["code"][0]
        return auth_code
