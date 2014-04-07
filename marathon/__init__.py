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
import httplib2
import json
import urllib
import logging
import argparse


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
stream = logging.StreamHandler()
stream.setFormatter(logFormatter)
logging.getLogger().addHandler(stream)
logger = logging.getLogger('py_marathon')


class Client(object):
    _client = None
    endpoint = None
    username = None
    password = None

    def __init__(self, endpoint, username=None, password=None):
        self.endpoint = endpoint.rstrip('/')

    @property
    def client(self):
        if self._client is None:
            self._client = httplib2.Http()
        return self._client

    def _make_request(self, resource, method="GET", body=None):
        resource = "%s%s" % (self.endpoint, resource)
        response, content = self.client.request(resource, method=method, body=body)
        return response, content

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
        response, content = self._make_request("/v2/apps", method='POST', body=json.dumps(body))
        logger.debug(response)
        logger.debug(content)
        return content

    def get_apps(self, cmd=None, app_id=None):
        vars = {}
        if cmd is not None:
            vars['cmd'] = cmd
        if app_id is not None:
            vars['id'] = app_id
        resource = "/v2/apps"
        if len(vars) > 1:
            vars = urllib.urlencode(vars)
            resource = "%s?%s" % (resource, vars)
        response, content = self._make_request(resource)
        logger.debug(response)
        logger.debug(content)
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

    def main(self, endpoint, username, password):
        c = Client(endpoint=endpoint, username=username, password=password)
        return c.get_apps()


if __name__ == '__main__':
    epilog = '''
    '''
    argparser = argparse.ArgumentParser(description='A simple AWS CloudTrail/Logstash SQS driven event loader',
                                        epilog=epilog)

    argparser.add_argument('--endpoint', '-E', type=str, help='the Marathon server endpoint', default='http://localhost:8080')
    argparser.add_argument('--username', '-U', type=str, help='the Marathon auth username', default=None)
    argparser.add_argument('--password', '-P', type=str, help='the Marathon auth password', default=None)
    argparser.add_argument('--debug', action='store_true', default=False)
    opts = argparser.parse_args()
    if opts.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info('py_marathon starting')
    logger.debug("startup options: %s" % opts.__dict__)

    Cli().main(opts.endpoint, opts.username, opts.password)
