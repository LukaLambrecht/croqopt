# import external modules
import requests
from random import randint
from re import findall


class ProxyRequests:
    def __init__(self, url):
        self.url = url
        self.sockets = []
        self.rdata = {
            'headers': {},
            'json': {},
            'status_code': 0,
            'timeout': 3.0,
            'errs': [
                'ConnectTimeout',
                'ProxyError',
                'SSLError',
                'ReadTimeout',
                'ConnectionError',
                'ConnectTimeoutError'
            ]
        }
        self.empty_warn = 'Proxy Pool has been emptied'
        self._acquire_sockets()

    def _acquire_sockets(self):
        r = requests.get('https://www.sslproxies.org/')
        matches = findall(r"<td>\d+\.\d+\.\d+\.\d+</td><td>\d+</td>", r.text)
        revised = [m.replace('<td>', '') for m in matches]
        self.sockets = [s[:-5].replace('</td>', ':') for s in revised]

    def _set_request_data(self, req, socket):
        self.rdata['request'] = req.text
        self.rdata['headers'] = req.headers
        self.rdata['status_code'] = req.status_code
        self.rdata['url'] = req.url
        self.rdata['raw'] = req.content
        self.rdata['proxy'] = socket
        try:
            self.rdata['json'] = req.json()
        except Exception as err:
            self.rdata['json'] = {type(err).__name__: str(err)}

    def _rand_sock(self):
        return randint(0, len(self.sockets) - 1)

    def _is_err(self, err):
        if type(err).__name__ not in self.rdata['errs']:
            raise err

    def _limit_succeeded(self):
        raise Exception(self.empty_warn)

    def get(self, params=None, headers=None):
        if len(self.sockets) > 0:
            current_socket = self.sockets.pop(self._rand_sock())
            proxies = {
                'http': 'http://' + current_socket,
                'https': 'https://' + current_socket
            }
            try:
                request = requests.get(
                    self.url,
                    timeout=self.rdata['timeout'],
                    proxies=proxies,
                    params=params,
                    headers=headers)
                self._set_request_data(request, current_socket)
            except Exception as e:
                self._is_err(e)
                self.get(params)
        else:
            self._limit_succeeded()

    def get_headers(self):
        return self.rdata['headers']

    def set_headers(self, outgoing_headers):
        self.rdata['headers'] = outgoing_headers

    def set_file(self, outgoing_file):
        self.rdata['file'] = outgoing_file

    def get_status_code(self):
        return self.rdata['status_code']

    def get_proxy_used(self):
        return self.rdata['proxy']

    def get_raw(self):
        return self.rdata['raw']

    def get_json(self):
        return self.rdata['json']

    def get_url(self):
        return self.rdata['url']

    def __str__(self):
        return str(self.rdata['request'])
