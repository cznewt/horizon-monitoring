
import requests
import json
import logging

from django.conf import settings

log = logging.getLogger('utils.kedb')

class Kedb(object):

    host = settings.KEDB_HOST
    port = settings.KEDB_PORT

    def __init__(self):
        pass

    def request(self, path, method="GET", params={}):
        log.debug("%s - %s - %s"%(method,path,params))

        if method == "GET":
            request = requests.get('%s%s' % (self.api, path))
        elif method == "POST":
            headers = {"Content-Type": "application/json" }
            request = requests.post('%s%s' % (self.api, path),data=json.dumps(params),headers=headers)
        
        if request.status_code in (200, 201):
            return request.json()
        else:
            """handle errors"""
#            messages.error(request, "%s - %s - %s - %s" % (method, path, params, request.status_code))
            return [{'id':1, 'name': request.status_code}, {'id':2, 'name': request.text}]

    @property
    def api(self):
        return 'http://%s:%s/api' % (self.host, self.port)

    @property
    def workaround_list(self):
        return self.request('/workarounds')

    @property
    def error_list(self):
        return self.request('/known-errors')

    def workaround_detail(self, workaround):
        url = '/workarounds/%s/' % (workaround)
        return requests.get(url)

    def error_detail(self, error):
        url = '/known-errors/%s/' % (error)
        return self.request(url)

    def error_create(self, error, data):
        url = '%s/known-errors' % self.api
        return self.request(url, "PUT", data)

    def error_update(self, error, data):
        url = '%s/known-errors/%s/' % (self.api, error)
        return self.request(url, "POST", data)

    def error_delete(self, error):
        url = '%s/api/known-errors/%s' % (self.api, error)
        response = requests.get(url)
        return response.json()

kedb_api = Kedb()
