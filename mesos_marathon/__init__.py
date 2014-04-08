"""
Apps
    POST /v2/apps: Create and start a new app
    GET /v2/apps: List all running apps
    GET /v2/apps?cmd={command}: List all running apps, filtered by command
    GET /v2/apps/{appId}: List the app appId
    GET /v2/apps/{appId}/versions: List the versions of the application with id appId.
    GET /v2/apps/{appId}/versions/{version}: List the configuration of the application with id appId at version version.
    PUT /v2/apps/{appId}: Change config of the app appId
    DELETE /v2/apps/{appId}: Destroy app appId
    GET /v2/apps/{appId}/tasks: List running tasks for app appId
    DELETE /v2/apps/{appId}/tasks?host={host}&scale={true|false}: kill tasks belonging to app appId
    DELETE /v2/apps/{appId}/tasks/{taskId}?scale={true|false}: Kill the task taskId that belongs to the application appId
Tasks
    GET /v2/tasks: List all running tasks
Event Subscriptions
    POST /v2/eventSubscriptions?callbackUrl={url}: Register a callback URL as an event subscriber
    GET /v2/eventSubscriptions: List all event subscriber callback URLs
    DELETE /v2/eventSubscriptions?callbackUrl={url} Unregister a callback URL from the event subscribers list
"""
from __future__ import absolute_import, print_function
import logging
import httplib2
import json
import urllib
from httplib import IncompleteRead

__version__ = '0.0.1'
log_formatter = logging.Formatter("%(message)s")
stream = logging.StreamHandler()
stream.setFormatter(log_formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream)


class ArgumentError(BaseException):
    def __init__(self, message=''):
        """
        :param message str:
        :return None:
        """
        self.message = message
        BaseException.__init__(self, message)


class Client(object):
    _client = None
    endpoint = None
    username = None
    password = None

    def __init__(self, endpoint, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        self.endpoint = endpoint.rstrip('/')

    @property
    def client(self):
        if self._client is None:
            self._client = httplib2.Http()
        return self._client

    def _make_request(self, resource, method="GET", body=None):
        headers = {'Accept': 'application/json'}
        resource = "%s%s" % (self.endpoint, resource)
        if self.username is not None:
            self.client.add_credentials(self.username, self.password)
        logger.debug([resource, method, body])
        if body is not None:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        try:
            response, content = self.client.request(resource, method=method, body=body, headers=headers)
            logger.debug({'response': response, 'content': content})
            if response.get('content-type') == 'application/json' and len(content) > 0:
                content = json.loads(content)
        except IncompleteRead as ex:
            logger.debug(ex)
            return {'status': 404, 'message': ex.message}, {}
        return response, content

    def create_app(self, app_id=None, cmd=None, cpus=1, mem=256, instances=1, executor=None, env=None, ports=None,
                   uris=None, constraints=None, **kwargs):
        if app_id is None:
            raise ArgumentError(message='app_id is required to update an app')
        if cmd is None:
            raise ArgumentError(message='cmd is required to update an app')
        logger.debug(kwargs)
        body = {'id': app_id, 'cmd': cmd, 'cpus': cpus, 'mem': mem,
                'instances': instances, 'ports': ports}
        if executor is not None:
            body['executor'] = executor
        if env is not None:
            if type(env) is not dict:
                raise ArgumentError(message="argument 'env' must be a list type:%s given" % type(env))
            body['env'] = env
        if ports is not None:
            if type(ports) is not list:
                raise ArgumentError(message="argument 'ports' must be a list with two members example: [80, 8080]")
            body['ports'] = ports
        else:
            body['ports'] = [0, 0]
        if uris is not None:
            if type(uris) is not list:
                raise ArgumentError(message="argument 'uris' must be a list")
            body['uris'] = env
        if constraints is not None:
            if type(constraints) is not list:
                raise ArgumentError(message="argument 'constraints' must be a list")
            body['constraints'] = constraints
        logger.debug(body)
        logger.debug(json.dumps(body))
        return self._make_request("/v2/apps", method='POST', body=json.dumps(body))

    def get_app(self, app_id=None, cmd=None, version=None, get_versions=False):
        resource = "/v2/apps"
        if app_id is not None:
            resource = "%s/%s" % (resource, app_id)
            if get_versions is True:
                resource = "%s/versions" % resource
            elif version is not None:
                resource = "%s/versions/%s" % (resource, version)
        elif version is not None:
            raise ArgumentError(message="app_id must be provided with version")
        elif cmd is not None:
            get_params = {'cmd': cmd}
            get_params = urllib.urlencode(get_params)
            resource = "%s?%s" % (resource, get_params)
        return self._make_request(resource)

    def delete_app(self, app_id=None):
        if app_id is None:
            raise ArgumentError(message="app_id must be provided with version")
        resource = "/v2/apps/%s" % app_id
        return self._make_request(resource, method='DELETE')

    def update_app(self, app_id, cmd, cpus=1, mem=256, instances=1, executor=None, env=None, ports=None,
                   uris=None, constraints=None, **kwargs):
        logger.debug(kwargs)
        if app_id is None:
            raise ArgumentError(message='app_id is required to update an app')
        resource = "/v2/apps/%s" % app_id
        body = {'id': app_id, 'cmd': cmd, 'cpus': cpus, 'mem': mem,
                'instances': instances, 'ports': ports}
        if executor is not None:
            body['executor'] = executor
        if env is not None:
            if type(env) is not dict:
                raise ArgumentError(message="argument 'env' must be a list type:%s given" % type(env))
            body['env'] = env
        if ports is not None:
            if type(ports) is not list:
                raise ArgumentError(message="argument 'ports' must be a list with two members example: [80, 8080]")
            body['ports'] = ports
        else:
            body['ports'] = [0, 0]
        if uris is not None:
            if type(uris) is not list:
                raise ArgumentError(message="argument 'uris' must be a list")
            body['uris'] = uris
        if constraints is not None:
            if type(constraints) is not list:
                raise ArgumentError(message="argument 'constraints' must be a list")
            body['constraints'] = constraints
        logger.debug(body)
        logger.debug(json.dumps(body))
        return self._make_request(resource=resource, method='PUT', body=json.dumps(body))

    def delete_tasks(self, app_id=None, host=None, scale=False, task_id=None, **kwargs):
        resource = ''
        if app_id is None:
            raise ArgumentError(message='app_id is required to update an app')
        if app_id is not None:
            resource = "/v2/apps/%s/tasks" % app_id
        if task_id is not None:
            resource = "%s/%s" % (resource, task_id)
        get_params = {'scale': 'true' if scale else 'false'}
        if host is not None:
            get_params['host'] = host
        if len(get_params) > 0:
            get_params = urllib.urlencode(get_params)
            resource = "%s?%s" % (resource, get_params)
        return self._make_request(resource=resource, method='DELETE')


    def get_tasks(self, app_id=None, **kwargs):
        if app_id is None:
            raise ArgumentError(message='app_id is required to update an app')
        resource = "/v2/apps/%s/tasks" % app_id
        return self._make_request(resource)

    def event_subscription(self, callback_uri=None, register=True, **kwargs):
        resource = "/v2/eventSubscriptions"
        req_method = "GET"
        if callback_uri is not None:
            get_params = {'callbackUrl': callback_uri}
            get_params = urllib.urlencode(get_params)
            resource = "%s?%s" % (resource, get_params)
            req_method = 'DELETE' if register else 'POST'
        return self._make_request(resource=resource, method=req_method)

