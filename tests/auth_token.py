from adm.adm import ADM
import sys

client_id = sys.argv[1]
client_secret = sys.argv[2]

client = ADM(client_id, client_secret)
print client.auth_token
