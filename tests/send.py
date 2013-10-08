from adm.adm import ADM
import sys

client_id = sys.argv[1]
client_secret = sys.argv[2]
registration_id = sys.argv[3]

url = None
if len(sys.argv) > 4:
    url = sys.argv[4]
    client = ADM(client_id, client_secret, url=url)
else:
    client = ADM(client_id, client_secret)

print client.send(registration_id, {'examplekey': {'key1': 'value1'}})
