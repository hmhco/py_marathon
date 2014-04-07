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
__author__ = 'allenr1'

import httplib2
from urllib import urlencode
import json

class App(object):
    cmd = None
    constraints = []
    container = {},
    cpus = 0
    env = {}
    executor = None
    id = None
    instances = 0
    mem = 0
    ports = []
    taskRateLimit = 1.0
    tasksRunning = 3
    tasksStaged = 0
    uris = []
    version = None


class Client(object):
    _client = None
    endpoint = None
    username = None
    password = None
    def __init__(self, endpoint="http://localhost:8080", username=None, password=None):
        self.endpoint = endpoint

    @property
    def client(self):
        if self._client is None:
            self._client = httplib2.Http()
        return self._client

    def _make_request(self, resource, method="GET"):
        resource = "%s/%s" % (self.endpoint, resource)
        return self.client.request(resource, method=method)

    def create_app(self, app_id, cmd, cpus=1, mem=256, instances=1, executor=None, env=None, ports=None,
                   uris=None, constraints=None, **kwargs):
        body = {'id': app_id, 'cmd': cmd, 'cpus': cpus, 'mem': mem, 'instances': instances, 'ports': [0, 0]}
        if executor is not None:
            body['executor'] = executor
        if env is not None:
            if env is not list:
                raise TypeError(message="argument 'env' must be a list", args=kwargs)
            body['env'] = env
        if ports is not None:
            if ports is not list:
                raise TypeError(message="argument 'ports' must be a list with two members example: [80, 8080]",
                                args=kwargs)
            body['ports'] = ports
        if uris is not None:
            if uris is not list:
                raise TypeError(message="argument 'uris' must be a list", args=kwargs)
            body['uris'] = env
        if constraints is not None:
            if constraints is not list:
                raise TypeError(message="argument 'constraints' must be a list", args=kwargs)
            body['constraints'] = env
        response, content = self.client.request("%s/v2/apps", method='POST', body=json.dumps(body))
        print response, content
        return content

    def get_apps(self, command=None, app_id=None):
        response, content = self.client.request("%s/v2/apps" % self.endpoint)
        if int(response.get('status')) == 200:
            if response.get('content-type') == 'application/json':
                content = json.loads(content)
        return content

    def get_app_versions(self, app_id=None, version=None):
        pass

    def update_app(self, app_id, config):
        pass

    def delete_tasks(self, app_id, host=None, scale=False, task_id=None):
        pass

    def get_tasks(self):
        pass

    def subscribe_event(self, callback_uri):
        pass

    def get_event_subsciptions(self):
        pass

    def delete_event_subscription(self, callback_uri):
        pass


class Cli(object):

    def main(self):
        pass


if __name__ == '__main__':
    pass
