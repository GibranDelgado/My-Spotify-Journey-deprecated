import base64
from requests import post
import json

def get_token(config_file):
    with open(config_file) as json_file:
        config_vars = json.load(json_file)
    
    client_id = config_vars['client_id']
    client_secret = config_vars['client_secret']
    
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    URL = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(URL, headers=headers, data=data)
    json_result = json.loads(result.content)
    
    return json_result["access_token"]