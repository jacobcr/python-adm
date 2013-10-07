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
