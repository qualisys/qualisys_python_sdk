import json

from functools import wraps

from twisted.internet import defer
from twisted.web.client import getPage
from twisted.web.error import Error


class RestError(Exception):
    def __init__(self, code, error):
        self.code = code
        self.error = error

    def __str__(self):
        return 'Error: {} - {}'.format(self.code, self.error)


def filter_function(result, filter):
    if filter in result:
        return {filter: result[filter]}
    return None


@defer.inlineCallbacks
def _get_page(self, method, url, data=None, verbose=False):
    if verbose:
        print("REST: " + method + " " + url + " " + str(data))

    try:
        response = yield getPage(url, method=method,
                                 headers={b'Content-Type': b'application/json'},
                                 postdata=data)
    except Error as e:
        raise RestError(int(e.status), e.response)
    except Exception as e:
        raise RestError(-1, str(e))

    try:
        obj = json.loads(response.decode('utf-8'))
    except Exception as e:
        raise RestError(-1, response)

    if verbose:
        print("REST: Response  " + obj)

    defer.returnValue(obj)


# rpc wrapper, only usable for QRest class members
def rest_endpoint(method, endpoint='/', filter=None):
    def rest_function_wrapper(f):
        @wraps(f)
        def rest_request(self, *args, **kwargs):

            # extract callbacks
            cb = kwargs.pop('on_ok', None)
            eb = kwargs.pop('on_error', None)

            # get data from function, if no data from function, see if we have a data parameter
            data = f(self, *args, **kwargs)
            if data is None:
                data = kwargs.pop('data', None)

            # try to get page
            d = _get_page(self, method.encode(), '{base}{endpoint}'.format(base=self.url, endpoint=endpoint).encode(),
                          data=json.dumps(data).encode(), verbose = self.verbose)

            if filter is not None:
                d.addCallback(filter_function, filter)

            if eb and cb:
                d.addCallbacks(cb, eb)
            elif eb:
                d.addErrback(eb)
            elif cb:
                d.addCallback(cb)

            return d

        return rest_request

    return rest_function_wrapper
