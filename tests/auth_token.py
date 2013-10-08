from adm.adm import ADM
import sys

client_id = sys.argv[1]
client_secret = sys.argv[2]

url = None
if len(sys.argv) > 3:
    url = sys.argv[3]
    client = ADM(client_id, client_secret, url=url)
else:
    client = ADM(client_id, client_secret)

print client.auth_token
