import human_curl as requests
from human_curl import exceptions
import urllib
import urlparse
import json
import time
import collections

ADM_URL = "https://api.amazon.com/"

class ADMException(Exception): pass
class ADMConnectionException(Exception): pass
class ADMBadRequestException(Exception): pass
class ADMAuthenticationException(Exception): pass


def flatten(d, parent_key=''):
    """ The data must be in the form of JSON-formatted key/value pairs; both keys and values MUST be String values. """
    items = []
    for k, v in d.items():
        new_key = parent_key + '_' + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

class ADM(object):
    def __init__(self, client_id, client_secret, url=ADM_URL, proxy=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = url
        self.url_auth = urlparse.urljoin(url, 'auth/O2/token')
        self.url_message = urlparse.urljoin(url, 'messaging/registrations/{0}/messages')
        if proxy:
            if isinstance(proxy, basestring):
                # from 'http://hostname:port'
                # to ('http',('hostname', port))
                protocol = url.split(':')[0]
                ip, port = proxy.split('/')[-1].split(':')
                proxy = (protocol, (ip, int(port)))

        self.proxy = proxy
        self._auth_token = None

    def send(self, registration_id, data):
        headers = {
            'Authorization' : 'Bearer {0}'.format(self.auth_token),
            'Content-Type': 'application/json',
            'X-Amzn-Type-Version': 'com.amazon.device.messaging.ADMMessage@1.0',
            'Accept': 'application/json',
            'X-Amzn-Accept-Type': 'com.amazon.device.messaging.ADMSendResult@1.0'
        }

        body = json.dumps({'data': flatten(data)})
        result = collections.defaultdict(dict)
        try:
            response = requests.post(self.url_message.format(registration_id), body, headers=headers, proxy=self.proxy)
        except exceptions.CurlError:
            raise ADMConnectionException("There was an internal error in the ADM server or in the network while trying to process the request")
        if response.status_code == 200:
            canonical = json.loads(response.content).get('registrationID')
            if canonical is not None and canonical != registration_id:
                result['canonical'][registration_id] = canonical
        elif response.status_code == 400:
            reason = json.loads(response.content).get('reason')
            if reason is not None and reason == 'InvalidRegistrationId':
                result['errors'][registration_id] = reason
            else:
                raise ADMException("Bad Request: {0}", response.content)
        elif response.status_code == 401:
            #internal auth token management fails, ensure next call recalculate it
            self._auth_token = None
            raise ADMException("Unable to refresh token: {0}", response.content)
        elif response.status_code == 413:
            raise ADMException("The payload provided exceeded the maximum allowable data size (6 KB): {0}", response.content)
        elif response.status_code == 429:
            raise ADMException("Maximum allowable rate reached: {0}", response.content)
        else:
            raise ADMException("Internal Server error: {0}{1}", response.status_code, response.content)

        return result


    @property
    def auth_token(self):
        # token is cached until it expires
        if self._auth_token is not None and time.time() - self._auth_expire < self._auth_timestamp:
            return self._auth_token

        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Charset': 'UTF-8',
        }
        body = urllib.urlencode({'grant_type': 'client_credentials',
                                   'scope': 'messaging:push',
                                   'client_id': self.client_id,
                                   'client_secret': self.client_secret})

        try:
            response = requests.post(self.url_auth, body, headers=headers, proxy=self.proxy)
        except exceptions.CurlError:
            raise ADMConnectionException("There was an internal error in the ADM server or in the network while trying to process the request")

        if response.status_code == 400:
            raise ADMBadRequestException("{0}:{1}".format(response.status_code, response.content))
        elif response.status_code == 401:
            raise ADMAuthenticationException("{0}:{1}".format(response.status_code, response.content))
        elif response.status_code != 200:
            raise ADMException("{0}:{1}".format(response.status_code, response.content))

        data = json.loads(response.content)
        # !! Using human_curl throught http proxy is not closing the socket properly, the performance will decrease due the number of
        # coonections opened.
        # With the explicit close the socket will remain TIME_WAIT until system timeout will expire it.
        response._curl_opener.close()
        self._auth_expire = data['expires_in']
        self._auth_timestamp = time.time()
        token = data['access_token']
        self._auth_token = token
        return token
