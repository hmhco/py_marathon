"""

"""
from __future__ import absolute_import, print_function
from . import __version__, logger, Client, ArgumentError
import argparse
import logging
import sys
from termcolor import colored


COMMAND_TEMPLATE = """    command: {cmd}
    cpu:{cpus}
    memory:{mem}/MB
    executor: {executor}
    ports: {ports}
    uris: {uris}
    environment: {env}
    constraints: {constraints}"""
COMMAND_TASK_TEMPLATE = """        Host           : {host}
        Staged At      : {stagedAt}
        Task Stated At : {startedAt}
        Ports:         : {ports}"""


def constraint_parser(constraints):
    """

    :param constraints str:
    :return list:
    """
    if constraints is None:
        return constraints
    result_list = []
    for constraint in constraints.split(','):
        result_list.append(constraint.split(':', 2))
    return result_list


def env_parser(option):
    """

    :param option str:
    :return dict:
    """
    if option is None:
        return option
    result_dict = {}
    for option in option.split(','):
        parts = option.split(':')
        result_dict[parts[0]] = parts[1]
    return result_dict


def uri_parser(option):
    """

    :param option str:
    :return list:
    """
    if option is None:
        return option
    result_list = []
    for option in option.split(','):
        result_list.append(str(option))
    return result_list


def ports_parser(option):
    """

    :param option str:
    :return list:
    """
    if option is None:
        return option
    result_list = []
    for option in option.split(','):
        result_list.append(int(option))
    return result_list


def main():
    """
    :return None:
    """
    argv = sys.argv
    epilog = '''
    Blah
    
    Blah
    
    Blah
    '''
    command_choices = ['create_app', 'get_app', 'update_app', 'delete_tasks', 'delete_app',
                       'get_tasks', 'event_subscription']
    argparser = argparse.ArgumentParser(description='A api wrapper for Mesos Marathon framework',
                                        epilog=epilog, add_help=False)

    argparser.add_argument('--endpoint', '-E', type=str, help='the Marathon server endpoint',
                           default='http://localhost:8080')
    argparser.add_argument('--username', '-U', type=str, help='the Marathon auth username', default=None)
    argparser.add_argument('--password', '-P', type=str, help='the Marathon auth password', default=None)
    argparser.add_argument('--version', '-v', action='store_true', default=False)
    argparser.add_argument('--json', action='store_true', default=False)
    argparser.add_argument('--debug', action='store_true', default=False)
    argparser.add_argument('command', nargs=1,
                           choices=command_choices)
    args = {}
    opts = {}
    if '--version' in argv:
        logger.info('py_marathon version: %s' % __version__)
        exit(0)
    if '--debug' in argv:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if 'get_app' in argv:
        argparser = argparse.ArgumentParser(parents=[argparser])
        argparser.add_argument('--cmd', type=str, help='the application command string (full or partial) to filter by',
                               default=None)
        argparser.add_argument('--app_id', type=str, help='the application id string', default=None)
        argparser.add_argument('--get_versions', action='store_true', default=False, help='the list app versions')
        argparser.add_argument('--app_version', type=str, help='the application id string', default=None)
        opts = argparser.parse_args()
        args = {'cmd': opts.cmd, 'app_id': opts.app_id, 'version': opts.app_version, 'get_versions': opts.get_versions}
    elif 'create_app' in argv or 'update_app' in argv:
        argparser.add_argument('--app_id', type=str, help='the application id string', required=True)
        argparser.add_argument('--cmd', type=str, help='the application command string', required=True)
        argparser.add_argument('--cpus', type=str, help='the application provisioned CPUs', default="0.1")
        argparser.add_argument('--mem', type=str, help='the applications memory provision', default="256")
        argparser.add_argument('--instances', type=str, help='the number on instances to scale to', default="1")
        argparser.add_argument('--executor', type=str, help='the command executor if none provided bash is used',
                               default=None)
        argparser.add_argument('--env', type=str, default=None,
                               help='the runtime environment, example HOME:/home/me,LD_LIBRARY_PATH:/usr/lib')
        argparser.add_argument('--ports', type=str, help='comma separated port lists 80,8080', default=None)
        argparser.add_argument('--uris', type=str, help='comma separated list of relevant URIs', default=None)
        argparser.add_argument('--constraints', type=str, help='the application command string', default=None)
        opts = argparser.parse_args()
        args = {'app_id': opts.app_id, 'cmd': opts.cmd, 'cpus': opts.cpus, 'mem': opts.mem, 'instances': opts.instances,
                'executor': opts.executor, 'env': env_parser(opts.env), 'ports': ports_parser(opts.ports),
                'uris': uri_parser(opts.uris), 'constraints': constraint_parser(opts.constraints)}
    elif 'delete_tasks' in argv:
        argparser.add_argument('--app_id', type=str, help='the application id string', required=True)
        argparser.add_argument('--host', type=str, help='the hostname to filter the request by')
        argparser.add_argument('--task_id', type=str, help='the hostname to filter the request by')
        argparser.add_argument('--scale', action='store_true', default=False,
                               help='If scale=true is specified, then the application is scaled down by the number'
                                    ' of killed tasks. ')
        opts = argparser.parse_args()
        args = {'app_id': opts.app_id, 'host': opts.host, 'scale': opts.scale, 'task_id': opts.task_id}
    elif 'delete_app' in argv:
        argparser.add_argument('--app_id', type=str, help='the application id string', required=True)
        opts = argparser.parse_args()
        args = {'app_id': opts.app_id}
    elif 'get_tasks' in argv:
        argparser.add_argument('--app_id', type=str, help='the application id string', required=True)
        opts = argparser.parse_args()
        args = {'app_id': opts.app_id}
    elif 'event_subscription' in argv:
        argparser.add_argument('--callback_uri', type=str, help='the event callback URI')
        argparser.add_argument('--register', action='store_false', default=True,
                               help='Register the URI or UnRegister the URI')
        opts = argparser.parse_args()
        args = {'callback_uri': opts.callback_uri, 'register': opts.register}
    else:
        argparser.parse_args()
        return exit(1)
    try:
        c = Client(endpoint=opts.endpoint, username=opts.username, password=opts.password)
        result, content = getattr(c, str(opts.command[0]))(**args)
    except ArgumentError as ae:
        print(colored(ae.message, 'red'))
        return exit(99)
    if opts.json is True:
        import json
        print(json.dumps({'_result': result, '_content': content if len(content) > 0 else {}}))
    elif 'apps' in content:
        for i in content['apps']:
            print(colored(i['id'], 'yellow'))
            print(colored(COMMAND_TEMPLATE.format(**i), 'cyan'))
    elif 'app' in content:
        print(colored(content['app']['id'], 'yellow'))
        print(colored(COMMAND_TEMPLATE.format(**content['app']), 'cyan'))
        if 'tasks' in content['app']:
            if len(content['app']['tasks']) > 0:
                print(colored("   Tasks:", 'yellow'))
            for task in content['app']['tasks']:
                print(colored("    %s" % task['id'], 'yellow'))
                print(colored(COMMAND_TASK_TEMPLATE.format(**task), 'white'))
    elif 'versions' in content:
        print(colored(opts.app_id, 'yellow'))
        for version in content['versions']:
            print(colored(version, 'cyan'))
    elif 'tasks' in content:
        print(colored("Tasks for: [%s]" % opts.app_id, 'yellow'))
        for task in content['tasks']:
            print(colored("    %s" % task['id'], 'yellow'))
            print(colored(COMMAND_TASK_TEMPLATE.format(**task), 'white'))
    elif len(content) == 0:
        if 200 >= int(result['status']) < 300:
            print(colored('SUCCESS', 'cyan'))
        elif int(result['status']) == 404:
            print(colored("Not Found", 'red'))
            exit(int(result['status']))
        else:
            print(colored('ERROR', 'red'))
            return exit(int(result['status']))
    else:
        print(content)

    return exit(0)


if __name__ == '__main__':
    main()
