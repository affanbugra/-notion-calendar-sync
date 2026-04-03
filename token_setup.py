"""
Bu script SADECE BİR KEZ çalıştırılır.
Google hesabınla tarayıcıda giriş yaparsın → token.json oluşur.
token.json içeriğini kopyalayıp GitHub Secret'a yapıştır.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

import json
token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes),
}

with open("token.json", "w") as f:
    json.dump(token_data, f, indent=2)

print("\n✅ token.json oluştu!")
print("Bu dosyanın tüm içeriğini kopyalayıp GOOGLE_TOKEN_JSON secret'ına yapıştır.\n")
