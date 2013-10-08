python-adm
==========

Python client for Amazon Device Messaging (ADM)

Usage
------------
Basic
```python
client = ADM(client_id, client_secret)
print client.send(registration_id, {'examplekey': {'key1': 'value1'}})
```

Error handling
```python
if 'errors' in response:
    for reg_id, reason in response['errors'].items():
        if error is 'InvalidRegistrationId':
            # Remove reg_ids from database
            pass

if 'canonical' in response:
    for reg_id, canonical_id in response['canonical'].items():
        # Repace reg_id with canonical_id in your database
        pass
```

Testing
======================

Library comes with a dummy server to make it easy testing your server
python tests/dummy_server.py

Responses
-------------
By default server will output ok responses but a results file can be defined.

Example file:
```
sometokentoresponseok,OK
sometokentobeupdated,UPDATE
sometokeninvalid,INVALID
```

Server will automatically load any resuts.csv file in the working dir.

Usage
--------------
```
pip install gevent
python tests/dummy_server.py
Starting server on 0.0.0.0:8081
```

Options
--------------
```
python dummy_server.py --help
Usage: dummy_server.py [options]

Options:
  -h, --help            show this help message and exit
  -p PORT, --port=PORT  Server port [8081]
  -b BIND, --bind_address=BIND
                        Bind addreess [0.0.0.0]
  -r RFILE, --results_file=RFILE
                        Results file [results.csv]
```
