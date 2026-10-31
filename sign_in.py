"""Run this yourself. It asks for your password, trades it for a one-hour session token, and saves only the token.
The password goes to the platform and nowhere else."""
import getpass, json, urllib.request
from host import URL

user = input("EARL username: ").strip()
password = getpass.getpass("EARL password: ")
req = urllib.request.Request(URL + "/api/auth/token", data=json.dumps({"username": user, "password": password}).encode(),
                             headers={"Content-Type": "application/json"})
token = json.load(urllib.request.urlopen(req))["access_token"]
with open(".session-token", "w") as f:
    f.write(token)
print("Saved to .session-token. It expires in one hour. Delete the file when you finish.")
