import uuid

import requests
from requests.exceptions import RequestException, Timeout

from widget.lib.widget_error import WidgetError


class GenericClient(object):
    def __init__(self, module_name, url, timeout=1000, token=None):
        self.module_name = module_name
        self.url = url
        self.timeout = timeout
        self.token = token

    def call_func(self, func_name, params, timeout=None):
        try:
            rpc = {
                "version": "1.1",
                "id": str(uuid.uuid4()),
                "params": params,
                "method": f"{self.module_name}.{func_name}"
            }
            timeout = (timeout or self.timeout) / 1000
            header = {}
            if self.token:
                header['authorization'] = self.token
            response = requests.post(self.url, json=rpc, timeout=timeout, headers=header)

            rpc_response = response.json()

            if 'error' in rpc_response:
                print('ERROR in call', rpc_response)
                raise WidgetError(
                    title = 'Call Error',
                    code = 'call-error',
                    message = str(rpc['error']['message'])
                )

            if 'result' not in rpc_response:
                return None

            result = rpc_response['result']

            if result is None:
                return None
            elif isinstance(result, list):
                return result
            else:
                raise WidgetError(
                    title = 'Incorrect Result Error',
                    code = 'incorrect-result-error',
                    message = 'The result is not a list or null'
                )

        except ConnectionError as cerr:
            raise WidgetError(
                title = 'Connection Error',
                code = 'connection-error',
                message = str(cerr)
            ) from cerr
        except Timeout as terr:
            raise WidgetError(
                title = 'Connection Error',
                code = 'connection-error',
                message = str(terr)
            ) from terr
        except RequestException as reqex:
            raise WidgetError(
                title = 'Request Error',
                code = 'request-error',
                message = str(reqex)
            ) from reqex
